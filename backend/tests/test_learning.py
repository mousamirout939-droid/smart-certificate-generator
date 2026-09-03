from tests.conftest import create_admin, create_employee, login
from app.models.course import Course


def _make_course(db, code="CRS-100", hours=10):
    course = Course(course_code=code, title="Test Course", category="General", duration_hours=hours)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_create_learning_record_recalculates_employee_hours(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-300", email="emp300@example.com", target_hours=20)
    course = _make_course(db_session, code="CRS-300", hours=10)
    headers = login(client, "admin@example.com")

    r = client.post("/api/learning", headers=headers, json={
        "employee_id": emp.id, "course_id": course.id,
        "learning_hours": 10, "completion_percentage": 100,
    })
    assert r.status_code == 201

    r2 = client.get(f"/api/employees/{emp.id}", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["employee"]["total_learning_hours"] == 10


def test_multiple_learning_records_sum_correctly(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-301", email="emp301@example.com", target_hours=50)
    c1 = _make_course(db_session, code="CRS-301", hours=10)
    c2 = _make_course(db_session, code="CRS-302", hours=15)
    c3 = _make_course(db_session, code="CRS-303", hours=30)
    headers = login(client, "admin@example.com")

    for course, hours in [(c1, 10), (c2, 15), (c3, 30)]:
        r = client.post("/api/learning", headers=headers, json={
            "employee_id": emp.id, "course_id": course.id,
            "learning_hours": hours, "completion_percentage": 100,
        })
        assert r.status_code == 201

    r = client.get(f"/api/employees/{emp.id}", headers=headers)
    body = r.json()
    assert body["employee"]["total_learning_hours"] == 55
    assert body["is_eligible"] is True  # 55 >= 50


def test_learning_hours_must_be_positive(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-302", email="emp302@example.com")
    course = _make_course(db_session, code="CRS-304")
    headers = login(client, "admin@example.com")

    r = client.post("/api/learning", headers=headers, json={
        "employee_id": emp.id, "course_id": course.id,
        "learning_hours": 0, "completion_percentage": 50,
    })
    assert r.status_code == 422


def test_completion_percentage_must_be_between_0_and_100(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-303", email="emp303@example.com")
    course = _make_course(db_session, code="CRS-305")
    headers = login(client, "admin@example.com")

    r = client.post("/api/learning", headers=headers, json={
        "employee_id": emp.id, "course_id": course.id,
        "learning_hours": 5, "completion_percentage": 150,
    })
    assert r.status_code == 422


def test_employee_can_only_view_own_learning_records(client, db_session):
    emp1 = create_employee(db_session, code="EMP-304", email="emp304@example.com")
    emp2 = create_employee(db_session, code="EMP-305", email="emp305@example.com")
    headers = login(client, "emp304@example.com")

    r = client.get(f"/api/learning/employee/{emp2.id}", headers=headers)
    assert r.status_code == 403

    r_own = client.get(f"/api/learning/employee/{emp1.id}", headers=headers)
    assert r_own.status_code == 200
