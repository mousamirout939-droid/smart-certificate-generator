from tests.conftest import create_employee, login
from app.models.course import Course
from app.models.enrollment import Enrollment, PaymentStatus


def _course(db, code, price=0):
    course = Course(course_code=code, title=code, duration_hours=10, price=price, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_learner_can_enroll_in_free_course_and_log_progress(client, db_session):
    employee = create_employee(db_session, email="free.learner@example.com")
    course = _course(db_session, "FREE-001")
    headers = login(client, employee.email)

    enrolled = client.post(f"/api/courses/{course.id}/enroll", headers=headers)
    assert enrolled.status_code == 200
    assert enrolled.json()["enrolled"] is True

    progress = client.post("/api/learning/me", headers=headers, json={
        "course_id": course.id, "learning_hours": 10, "completion_percentage": 100,
    })
    assert progress.status_code == 201
    assert progress.json()["status"] == "completed"


def test_paid_course_requires_checkout_and_cannot_accept_progress(client, db_session):
    employee = create_employee(db_session, email="paid.learner@example.com")
    course = _course(db_session, "PAID-001", price=49.99)
    headers = login(client, employee.email)

    enrolled = client.post(f"/api/courses/{course.id}/enroll", headers=headers)
    assert enrolled.status_code == 200
    assert enrolled.json()["checkout_required"] is True

    progress = client.post("/api/learning/me", headers=headers, json={
        "course_id": course.id, "learning_hours": 1, "completion_percentage": 10,
    })
    assert progress.status_code == 403


def test_paid_enrollment_allows_progress_after_payment_confirmation(client, db_session):
    employee = create_employee(db_session, email="confirmed.learner@example.com")
    course = _course(db_session, "PAID-002", price=25)
    enrollment = Enrollment(employee_id=employee.id, course_id=course.id, amount=25, payment_status=PaymentStatus.PAID)
    db_session.add(enrollment)
    db_session.commit()
    headers = login(client, employee.email)

    progress = client.post("/api/learning/me", headers=headers, json={
        "course_id": course.id, "learning_hours": 2, "completion_percentage": 25,
    })
    assert progress.status_code == 201


def test_all_lessons_are_required_before_named_course_certificate(client, db_session):
    employee = create_employee(db_session, name="Certificate Learner", email="certificate.learner@example.com")
    course = _course(db_session, "VIDEO-001")
    course.videos = [
        {"id": "lesson-one", "title": "Lesson One", "youtube_id": "abc123"},
        {"id": "lesson-two", "title": "Lesson Two", "youtube_id": "def456"},
    ]
    db_session.commit()
    headers = login(client, employee.email)
    assert client.post(f"/api/courses/{course.id}/enroll", headers=headers).status_code == 200

    blocked = client.post(f"/api/courses/{course.id}/complete", headers=headers)
    assert blocked.status_code == 400

    for video_id in ["lesson-one", "lesson-two"]:
        watched = client.post(f"/api/courses/{course.id}/videos/{video_id}/watched", headers=headers)
        assert watched.status_code == 200

    completed = client.post(f"/api/courses/{course.id}/complete", headers=headers)
    assert completed.status_code == 200
    certificates = client.get("/api/certificates", headers=headers)
    assert certificates.status_code == 200
    assert certificates.json()[0]["achievement_type"] == "COURSE_COMPLETION"


def test_course_quiz_requires_80_percent_before_certificate(client, db_session):
    employee = create_employee(db_session, name="Quiz Learner", email="quiz.learner@example.com")
    course = _course(db_session, "QUIZ-001")
    course.videos = [{"id": "lesson-one", "title": "Lesson One", "youtube_id": "abc123"}]
    course.quiz_questions = [
        {"id": f"q{index}", "question": f"Question {index}", "options": ["Correct", "Wrong"], "correct_option": "Correct"}
        for index in range(1, 6)
    ]
    db_session.commit()
    headers = login(client, employee.email)
    assert client.post(f"/api/courses/{course.id}/enroll", headers=headers).status_code == 200
    assert client.post(f"/api/courses/{course.id}/videos/lesson-one/watched", headers=headers).status_code == 200

    quiz = client.get(f"/api/courses/{course.id}/quiz", headers=headers)
    assert quiz.status_code == 200
    question_ids = [question["id"] for question in quiz.json()]

    failed = client.post(f"/api/courses/{course.id}/quiz", headers=headers, json={"answers": {
        question_id: "Correct" if index < 3 else "Wrong"
        for index, question_id in enumerate(question_ids)
    }})
    assert failed.status_code == 200
    assert failed.json()["passed"] is False
    assert client.post(f"/api/courses/{course.id}/complete", headers=headers).status_code == 400

    passed = client.post(f"/api/courses/{course.id}/quiz", headers=headers, json={"answers": {
        question_id: "Correct" for question_id in question_ids
    }})
    assert passed.json()["passed"] is True
    assert client.post(f"/api/courses/{course.id}/complete", headers=headers).status_code == 200