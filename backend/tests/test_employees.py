from tests.conftest import create_admin, create_employee, login


def test_create_employee_as_admin(client, db_session):
    create_admin(db_session)
    headers = login(client, "admin@example.com")
    r = client.post("/api/employees", headers=headers, json={
        "employee_code": "EMP-200", "full_name": "Jane Doe", "email": "jane.doe@example.com",
        "department": "Sales", "target_hours": 40, "password": "Password123!",
    })
    assert r.status_code == 201
    assert r.json()["employee_code"] == "EMP-200"
    assert r.json()["total_learning_hours"] == 0


def test_create_duplicate_employee_code_rejected(client, db_session):
    create_admin(db_session)
    headers = login(client, "admin@example.com")
    payload = {
        "employee_code": "EMP-201", "full_name": "First", "email": "first@example.com",
        "target_hours": 40, "password": "Password123!",
    }
    r1 = client.post("/api/employees", headers=headers, json=payload)
    assert r1.status_code == 201

    payload2 = dict(payload, email="second@example.com")
    r2 = client.post("/api/employees", headers=headers, json=payload2)
    assert r2.status_code == 400


def test_create_duplicate_employee_email_rejected(client, db_session):
    create_admin(db_session)
    headers = login(client, "admin@example.com")
    payload = {
        "employee_code": "EMP-202", "full_name": "First", "email": "dup@example.com",
        "target_hours": 40, "password": "Password123!",
    }
    r1 = client.post("/api/employees", headers=headers, json=payload)
    assert r1.status_code == 201

    payload2 = dict(payload, employee_code="EMP-203")
    r2 = client.post("/api/employees", headers=headers, json=payload2)
    assert r2.status_code == 400


def test_employee_cannot_create_employee(client, db_session):
    create_employee(db_session, code="EMP-204", email="emp204@example.com")
    headers = login(client, "emp204@example.com")
    r = client.post("/api/employees", headers=headers, json={
        "employee_code": "EMP-205", "full_name": "X", "email": "x@example.com",
        "target_hours": 40, "password": "Password123!",
    })
    assert r.status_code == 403


def test_employee_cannot_view_another_employee(client, db_session):
    emp1 = create_employee(db_session, code="EMP-206", email="emp206@example.com")
    emp2 = create_employee(db_session, code="EMP-207", email="emp207@example.com")
    headers = login(client, "emp206@example.com")

    r = client.get(f"/api/employees/{emp2.id}", headers=headers)
    assert r.status_code == 403

    r_own = client.get(f"/api/employees/{emp1.id}", headers=headers)
    assert r_own.status_code == 200


def test_admin_can_deactivate_employee(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-208", email="emp208@example.com")
    headers = login(client, "admin@example.com")

    r = client.delete(f"/api/employees/{emp.id}", headers=headers)
    assert r.status_code == 204

    # Deactivated employee's user account can no longer log in
    r_login = client.post("/api/auth/login", json={"email": "emp208@example.com", "password": "Password123!"})
    assert r_login.status_code == 403
