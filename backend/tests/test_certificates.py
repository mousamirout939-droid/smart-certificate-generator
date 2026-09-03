from tests.conftest import create_admin, create_employee, login
from app.services.automation_service import generate_certificate_for_employee
from app.models.employee import Employee


def test_manual_certificate_generation_requires_target_reached(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-400", email="emp400@example.com", target_hours=50, total_hours=30)
    headers = login(client, "admin@example.com")

    r = client.post(f"/api/certificates/generate/{emp.id}", headers=headers)
    assert r.status_code == 400


def test_manual_certificate_generation_succeeds_when_eligible(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-401", email="emp401@example.com", target_hours=50, total_hours=55)
    headers = login(client, "admin@example.com")

    r = client.post(f"/api/certificates/generate/{emp.id}", headers=headers)
    assert r.status_code == 201
    body = r.json()
    assert body["certificate_id"].startswith("CERT-")
    assert body["achieved_hours"] == 55
    assert body["target_hours"] == 50
    assert body["email_sent"] is False  # SMTP disabled in test env
    assert body["email_failure_reason"] is not None


def test_certificate_ids_are_unique(db_session):
    emp1 = create_employee(db_session, code="EMP-402", email="emp402@example.com", target_hours=10, total_hours=10)
    emp2 = create_employee(db_session, code="EMP-403", email="emp403@example.com", target_hours=10, total_hours=10)

    cert1, outcome1 = generate_certificate_for_employee(db_session, emp1)
    cert2, outcome2 = generate_certificate_for_employee(db_session, emp2)

    assert outcome1 == "created"
    assert outcome2 == "created"
    assert cert1.certificate_id != cert2.certificate_id


def test_duplicate_certificate_prevented_for_same_employee_and_target(db_session):
    emp = create_employee(db_session, code="EMP-404", email="emp404@example.com", target_hours=10, total_hours=10)

    cert1, outcome1 = generate_certificate_for_employee(db_session, emp)
    assert outcome1 == "created"

    # Attempting again for the exact same achievement must be skipped, not duplicated.
    cert2, outcome2 = generate_certificate_for_employee(db_session, emp)
    assert outcome2 == "skipped_existing"
    assert cert2 is None

    from app.models.certificate import Certificate
    count = db_session.query(Certificate).filter(Certificate.employee_id == emp.id).count()
    assert count == 1


def test_manual_generate_endpoint_returns_409_on_duplicate(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-405", email="emp405@example.com", target_hours=10, total_hours=10)
    headers = login(client, "admin@example.com")

    r1 = client.post(f"/api/certificates/generate/{emp.id}", headers=headers)
    assert r1.status_code == 201

    r2 = client.post(f"/api/certificates/generate/{emp.id}", headers=headers)
    assert r2.status_code == 409


def test_employee_cannot_access_another_employees_certificate(client, db_session):
    emp1 = create_employee(db_session, code="EMP-406", email="emp406@example.com", target_hours=10, total_hours=10)
    emp2 = create_employee(db_session, code="EMP-407", email="emp407@example.com", target_hours=10, total_hours=10)

    cert1, _ = generate_certificate_for_employee(db_session, emp1)

    headers_emp2 = login(client, "emp407@example.com")
    r = client.get(f"/api/certificates/{cert1.id}", headers=headers_emp2)
    assert r.status_code == 403

    r_download = client.get(f"/api/certificates/{cert1.id}/download", headers=headers_emp2)
    assert r_download.status_code == 403


def test_employee_can_access_own_certificate_and_download_pdf(client, db_session):
    emp = create_employee(db_session, code="EMP-408", email="emp408@example.com", target_hours=10, total_hours=10)
    cert, _ = generate_certificate_for_employee(db_session, emp)

    headers = login(client, "emp408@example.com")
    r = client.get(f"/api/certificates/{cert.id}", headers=headers)
    assert r.status_code == 200

    r_download = client.get(f"/api/certificates/{cert.id}/download", headers=headers)
    assert r_download.status_code == 200
    assert r_download.headers["content-type"] == "application/pdf"
    assert len(r_download.content) > 0


def test_certificate_verification_endpoint_returns_public_certificate_details(client, db_session):
    emp = create_employee(db_session, code="EMP-410", email="emp410@example.com", target_hours=10, total_hours=10)
    cert, _ = generate_certificate_for_employee(db_session, emp)

    response = client.get(f"/api/certificates/verify/{cert.certificate_id}")
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["learner_name"] == emp.full_name


def test_admin_can_resend_certificate_email(client, db_session):
    create_admin(db_session)
    emp = create_employee(db_session, code="EMP-409", email="emp409@example.com", target_hours=10, total_hours=10)
    cert, _ = generate_certificate_for_employee(db_session, emp)

    headers = login(client, "admin@example.com")
    r = client.post(f"/api/certificates/{cert.id}/resend", headers=headers)
    assert r.status_code == 200
    # SMTP disabled in test env, so still pending, but request should succeed cleanly
    assert r.json()["email_sent"] is False
