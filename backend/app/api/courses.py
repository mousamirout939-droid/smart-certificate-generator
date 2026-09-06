from typing import Optional
import random

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.course import Course
from app.models.user import User
from app.models.employee import Employee
from app.models.enrollment import Enrollment, EnrollmentStatus, PaymentStatus
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut, QuizQuestionOut, QuizSubmission, QuizResult
from app.schemas.enrollment import EnrollmentActionOut, EnrollmentOut
from app.services.automation_service import run_automation, generate_course_certificate
from app.models.learning_record import LearningRecord, LearningStatus
from app.services.learning_calc import recalculate_employee_hours
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/courses", tags=["courses"])


def _employee_for_user(current_user: User, db: Session):
    if not current_user.employee_id:
        raise HTTPException(status_code=403, detail="Only learner accounts can enroll in courses")
    employee = db.query(Employee).filter(Employee.id == current_user.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return employee


def _enrolled_course(course_id: int, current_user: User, db: Session):
    employee = _employee_for_user(current_user, db)
    course = db.query(Course).filter(Course.id == course_id, Course.is_active.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Active course not found")
    enrollment = db.query(Enrollment).filter(
        Enrollment.employee_id == employee.id, Enrollment.course_id == course.id,
        Enrollment.status != EnrollmentStatus.CANCELLED,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Enroll in this course before accessing its lessons")
    if enrollment.payment_status not in [PaymentStatus.NOT_REQUIRED, PaymentStatus.PAID]:
        raise HTTPException(status_code=402, detail="Payment is required before accessing this course")
    return employee, course, enrollment


@router.get("", response_model=list[CourseOut])
def list_courses(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Course)
    if search:
        like = f"%{search}%"
        query = query.filter((Course.title.ilike(like)) | (Course.course_code.ilike(like)))
    return query.order_by(Course.id.desc()).all()


@router.get("/enrollments/me", response_model=list[EnrollmentOut])
def my_enrollments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = _employee_for_user(current_user, db)
    return db.query(Enrollment).filter(Enrollment.employee_id == employee.id).order_by(Enrollment.id.desc()).all()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, course, _ = _enrolled_course(course_id, current_user, db)
    return course


@router.post("/{course_id}/videos/{video_id}/watched", response_model=EnrollmentOut)
def mark_video_watched(course_id: int, video_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, course, enrollment = _enrolled_course(course_id, current_user, db)
    video_ids = {str(video.get("id")) for video in (course.videos or [])}
    if video_id not in video_ids:
        raise HTTPException(status_code=404, detail="Lesson not found")
    watched = list(enrollment.watched_video_ids or [])
    if video_id not in watched:
        watched.append(video_id)
        enrollment.watched_video_ids = watched
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
    return enrollment


@router.get("/{course_id}/quiz", response_model=list[QuizQuestionOut])
def get_course_quiz(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, course, enrollment = _enrolled_course(course_id, current_user, db)
    questions = [question for question in (course.quiz_questions or []) if question.get("id") and question.get("question") and question.get("options")]
    if len(questions) < 5:
        raise HTTPException(status_code=400, detail="This course does not have five quiz questions yet")
    selected_ids = [str(question_id) for question_id in (enrollment.selected_quiz_question_ids or [])]
    if len(selected_ids) != 5 or set(selected_ids) != {str(question["id"]) for question in questions if str(question["id"]) in selected_ids}:
        selected_ids = [str(question["id"]) for question in random.sample(questions, 5)]
        enrollment.selected_quiz_question_ids = selected_ids
        db.add(enrollment)
        db.commit()
    selected = {str(question["id"]): question for question in questions if str(question["id"]) in selected_ids}
    if len(selected) != 5:
        enrollment.selected_quiz_question_ids = []
        db.add(enrollment)
        db.commit()
        return get_course_quiz(course_id, db, current_user)
    return [QuizQuestionOut(id=question_id, question=selected[question_id]["question"], options=selected[question_id]["options"]) for question_id in selected_ids]


@router.post("/{course_id}/quiz", response_model=QuizResult)
def submit_course_quiz(course_id: int, payload: QuizSubmission, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, course, enrollment = _enrolled_course(course_id, current_user, db)
    required = {str(video.get("id")) for video in (course.videos or [])}
    if required - set(enrollment.watched_video_ids or []):
        raise HTTPException(status_code=400, detail="Watch every lesson before taking the quiz")
    questions = {str(question.get("id")): question for question in (course.quiz_questions or []) if question.get("id")}
    selected_ids = [str(question_id) for question_id in (enrollment.selected_quiz_question_ids or [])]
    if len(selected_ids) != 5 or any(question_id not in questions for question_id in selected_ids):
        raise HTTPException(status_code=400, detail="Start the quiz before submitting answers")
    if set(payload.answers) != set(selected_ids):
        raise HTTPException(status_code=400, detail="Answer all five quiz questions")
    correct = sum(payload.answers[question_id] == str(questions[question_id].get("correct_option")) for question_id in selected_ids)
    score = correct / 5 * 100
    enrollment.quiz_score = score
    enrollment.quiz_passed = score >= 80
    db.add(enrollment)
    db.commit()
    return QuizResult(score=score, passed=enrollment.quiz_passed, correct_answers=correct, total_questions=5)


@router.post("/{course_id}/complete", response_model=EnrollmentOut)
def complete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee, course, enrollment = _enrolled_course(course_id, current_user, db)
    required = {str(video.get("id")) for video in (course.videos or [])}
    if not required:
        raise HTTPException(status_code=400, detail="This course has no lessons yet")
    watched = set(enrollment.watched_video_ids or [])
    if required - watched:
        raise HTTPException(status_code=400, detail="Watch every lesson before completing this course")
    if course.quiz_questions and not enrollment.quiz_passed:
        raise HTTPException(status_code=400, detail="Pass the five-question quiz with at least 80% before completing this course")
    if enrollment.status == EnrollmentStatus.COMPLETED:
        return enrollment

    enrollment.status = EnrollmentStatus.COMPLETED
    record = LearningRecord(
        employee_id=employee.id,
        course_id=course.id,
        learning_hours=course.duration_hours,
        completion_percentage=100,
        status=LearningStatus.COMPLETED,
    )
    db.add(record)
    db.commit()
    recalculate_employee_hours(db, employee.id)
    generate_course_certificate(db, employee, course.id, course.duration_hours, course.title)
    run_automation(db)
    db.refresh(enrollment)
    return enrollment


@router.post("/{course_id}/enroll", response_model=EnrollmentActionOut)
def enroll_in_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = _employee_for_user(current_user, db)
    course = db.query(Course).filter(Course.id == course_id, Course.is_active.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Active course not found")

    existing = db.query(Enrollment).filter(
        Enrollment.employee_id == employee.id, Enrollment.course_id == course.id,
    ).first()
    if existing:
        return EnrollmentActionOut(enrolled=True, message="You are already enrolled", enrollment=existing)
    if course.price > 0:
        return EnrollmentActionOut(
            enrolled=False,
            checkout_required=True,
            message="This course requires payment. Connect a payment provider to continue.",
        )

    enrollment = Enrollment(
        employee_id=employee.id,
        course_id=course.id,
        amount=0,
        payment_status=PaymentStatus.NOT_REQUIRED,
        status=EnrollmentStatus.ACTIVE,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return EnrollmentActionOut(enrolled=True, message="Enrollment confirmed", enrollment=enrollment)


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(Course).filter(Course.course_code == payload.course_code).first():
        raise HTTPException(status_code=400, detail="Course code already exists")

    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(course, field, value)

    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_course(course_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.is_active = False
    db.add(course)
    db.commit()
    return None
