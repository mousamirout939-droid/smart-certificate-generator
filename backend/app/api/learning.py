from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.learning_record import LearningRecord, LearningStatus
from app.models.employee import Employee
from app.models.course import Course
from app.models.user import User, UserRole
from app.models.enrollment import Enrollment, EnrollmentStatus, PaymentStatus
from app.schemas.learning import LearningRecordCreate, LearnerLearningRecordCreate, LearningRecordOut
from app.services.learning_calc import recalculate_employee_hours
from app.services.automation_service import run_automation
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.post("/me", response_model=LearningRecordOut, status_code=status.HTTP_201_CREATED)
def create_my_learning_record(
    payload: LearnerLearningRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee_id:
        raise HTTPException(status_code=403, detail="Only learner accounts can submit progress")
    enrollment = db.query(Enrollment).filter(
        Enrollment.employee_id == current_user.employee_id,
        Enrollment.course_id == payload.course_id,
        Enrollment.status.in_([EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]),
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Enroll in this course before submitting progress")
    if enrollment.payment_status not in [PaymentStatus.NOT_REQUIRED, PaymentStatus.PAID]:
        raise HTTPException(status_code=402, detail="Payment is required before accessing this course")

    record = LearningRecord(
        employee_id=current_user.employee_id,
        course_id=payload.course_id,
        learning_hours=payload.learning_hours,
        completion_percentage=payload.completion_percentage,
        completion_date=payload.completion_date,
        status=LearningStatus.COMPLETED if payload.completion_percentage >= 100 else LearningStatus.IN_PROGRESS,
    )
    if payload.completion_percentage >= 100:
        enrollment.status = EnrollmentStatus.COMPLETED
    db.add(record)
    db.commit()
    db.refresh(record)
    recalculate_employee_hours(db, current_user.employee_id)
    if payload.completion_percentage >= 100:
        run_automation(db)
    return record


@router.get("", response_model=list[LearningRecordOut])
def list_learning_records(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(LearningRecord).order_by(LearningRecord.id.desc()).all()


@router.post("", response_model=LearningRecordOut, status_code=status.HTTP_201_CREATED)
def create_learning_record(
    payload: LearningRecordCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    record = LearningRecord(
        employee_id=payload.employee_id,
        course_id=payload.course_id,
        learning_hours=payload.learning_hours,
        completion_percentage=payload.completion_percentage,
        completion_date=payload.completion_date,
        status=LearningStatus.COMPLETED if payload.completion_percentage >= 100 else LearningStatus.IN_PROGRESS,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Recalculate employee's total hours from source of truth (learning_records)
    recalculate_employee_hours(db, payload.employee_id)

    return record


@router.get("/employee/{employee_id}", response_model=list[LearningRecordOut])
def get_employee_learning_records(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN and current_user.employee_id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return (
        db.query(LearningRecord)
        .filter(LearningRecord.employee_id == employee_id)
        .order_by(LearningRecord.id.desc())
        .all()
    )
