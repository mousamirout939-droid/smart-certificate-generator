from tests.conftest import create_employee
from app.services.automation_service import run_automation
from app.models.certificate import Certificate


def test_target_detection_only_flags_employees_who_reached_target(db_session):
    create_employee(db_session, code="EMP-500", email="emp500@example.com", target_hours=50, total_hours=52)  # eligible
    create_employee(db_session, code="EMP-501", email="emp501@example.com", target_hours=50, total_hours=30)  # not eligible

    result = run_automation(db_session)

    assert result["checked_employees"] == 2
    assert result["newly_eligible"] == 1
    assert result["certificates_created"] == 1


def test_automation_run_once_creates_one_certificate(db_session):
    create_employee(db_session, code="EMP-502", email="emp502@example.com", target_hours=50, total_hours=52)

    result = run_automation(db_session)
    assert result["certificates_created"] == 1

    count = db_session.query(Certificate).count()
    assert count == 1


def test_automation_run_repeatedly_does_not_duplicate():
    """
    This is the most important requirement per spec:
    Run automation once -> 1 certificate. Run automation again -> still 1 certificate.
    """
    from tests.conftest import SessionLocal
    db = SessionLocal()
    try:
        create_employee(db, code="EMP-503", email="emp503@example.com", target_hours=50, total_hours=52)

        result1 = run_automation(db)
        assert result1["certificates_created"] == 1
        assert db.query(Certificate).count() == 1

        result2 = run_automation(db)
        assert result2["certificates_created"] == 0
        assert result2["certificates_skipped_existing"] == 1
        assert db.query(Certificate).count() == 1

        # Run it 10 times total for extra safety, per spec.
        for _ in range(8):
            run_automation(db)

        assert db.query(Certificate).count() == 1
    finally:
        db.close()


def test_inactive_employees_are_excluded_from_automation(db_session):
    emp = create_employee(db_session, code="EMP-504", email="emp504@example.com", target_hours=50, total_hours=60)
    emp.status = "inactive"
    db_session.add(emp)
    db_session.commit()

    result = run_automation(db_session)
    assert result["checked_employees"] == 0
    assert result["certificates_created"] == 0


def test_automation_handles_email_not_configured_gracefully(db_session):
    """SMTP is disabled in the test environment (see conftest). Certificate
    generation must still succeed, just marked as email pending."""
    create_employee(db_session, code="EMP-505", email="emp505@example.com", target_hours=50, total_hours=52)

    result = run_automation(db_session)
    assert result["certificates_created"] == 1
    assert result["emails_sent"] == 0
    assert result["emails_pending"] == 1

    cert = db_session.query(Certificate).first()
    assert cert is not None
    assert cert.email_sent is False
    assert cert.email_failure_reason is not None


def test_automation_endpoint_requires_admin(client, db_session):
    from tests.conftest import login
    create_employee(db_session, code="EMP-506", email="emp506@example.com")
    headers = login(client, "emp506@example.com")

    r = client.post("/api/automation/run", headers=headers)
    assert r.status_code == 403
