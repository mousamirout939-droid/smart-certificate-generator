"""
Automation service.

This is the ONLY place that decides whether a certificate should be
generated. API routes must call into this service rather than
re-implementing eligibility/duplicate-prevention logic themselves.

Idempotency guarantee: running run_automation() N times must produce
exactly the same certificates as running it once. This is enforced two
ways:
  1. Application-level check: query for an existing certificate with the
     same (employee_id, achievement_type, target_hours) before creating.
  2. Database-level UniqueConstraint on certificates as a hard backstop,
     in case of a race condition between the check and the insert.
"""
import logging
from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.employee import Employee, EmployeeStatus
from app.models.certificate import Certificate
from app.utils.certificate_utils import generate_certificate_id
from app.services.certificate_service import generate_certificate_pdf
from app.services.email_service import send_certificate_email

logger = logging.getLogger("app.automation")

ACHIEVEMENT_TYPE = "LEARNING_TARGET"


def _find_existing_certificate(db: Session, employee_id: int, target_hours: float, achievement_type: str = ACHIEVEMENT_TYPE, course_id: int | None = None) -> Certificate | None:
    return (
        db.query(Certificate)
        .filter(
            Certificate.employee_id == employee_id,
            Certificate.achievement_type == achievement_type,
            Certificate.target_hours == target_hours,
            Certificate.course_id == course_id,
        )
        .first()
    )


def generate_certificate_for_employee(db: Session, employee: Employee, *, target_hours: float | None = None, achievement_type: str = ACHIEVEMENT_TYPE, course_id: int | None = None, course_title: str | None = None) -> tuple[Certificate | None, str]:
    """
    Attempts to create+persist a certificate for an already-eligible employee.

    Returns (certificate_or_none, status_message). Never raises: any
    failure (duplicate, PDF error, email error) is captured and reported.
    """
    certificate_target = target_hours if target_hours is not None else employee.target_hours
    existing = _find_existing_certificate(db, employee.id, certificate_target, achievement_type, course_id)
    if existing:
        return None, "skipped_existing"

    certificate_id = generate_certificate_id(db)
    issue_date = date.today()

    try:
        pdf_path = generate_certificate_pdf(
            employee_full_name=employee.full_name,
            employee_code=employee.employee_code,
            certificate_id=certificate_id,
            achieved_hours=employee.total_learning_hours,
            target_hours=certificate_target,
            issue_date_str=issue_date.strftime("%B %d, %Y"),
            course_title=course_title,
        )
    except Exception as e:  # noqa: BLE001
        logger.error("PDF generation failed for employee_id=%s: %s", employee.id, e)
        return None, f"pdf_generation_failed: {e}"

    certificate = Certificate(
        certificate_id=certificate_id,
        employee_id=employee.id,
        achievement_type=achievement_type,
        course_id=course_id,
        target_hours=certificate_target,
        achieved_hours=employee.total_learning_hours,
        issue_date=issue_date,
        pdf_path=pdf_path,
        email_sent=False,
    )

    try:
        db.add(certificate)
        db.commit()
        db.refresh(certificate)
    except IntegrityError:
        # Backstop: a race condition slipped a duplicate past our earlier
        # application-level check. Roll back and treat as already-existing.
        db.rollback()
        logger.warning("Duplicate certificate insert prevented at DB level for employee_id=%s", employee.id)
        return None, "skipped_existing"

    # Attempt email delivery. Failure never deletes the certificate or
    # crashes the request/job - it's recorded on the record for retry.
    result = send_certificate_email(
        to_email=employee.email,
        employee_name=employee.full_name,
        achieved_hours=certificate.achieved_hours,
        target_hours=certificate.target_hours,
        certificate_id=certificate.certificate_id,
        pdf_path=certificate.pdf_path,
    )

    certificate.email_sent = result.sent
    certificate.email_sent_at = datetime.utcnow() if result.sent else None
    certificate.email_failure_reason = None if result.sent else result.reason
    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    logger.info(
        "Certificate %s created for employee_id=%s (email_sent=%s)",
        certificate.certificate_id, employee.id, certificate.email_sent,
    )
    return certificate, "created"


def generate_course_certificate(db: Session, employee: Employee, course_id: int, duration_hours: float, course_title: str | None = None) -> tuple[Certificate | None, str]:
    return generate_certificate_for_employee(
        db,
        employee,
        target_hours=duration_hours,
        achievement_type="COURSE_COMPLETION",
        course_id=course_id,
        course_title=course_title,
    )


def run_automation(db: Session) -> dict:
    """
    Full automation pass:
      1. Find active employees.
      2. Their total_learning_hours (kept up to date by learning record
         creation) is compared against their target_hours.
      3. For newly eligible employees without an existing certificate,
         generate one + send email.

    Safe to call repeatedly - see module docstring.
    """
    active_employees = db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE).all()

    checked = 0
    newly_eligible = 0
    created = 0
    skipped_existing = 0
    emails_sent = 0
    emails_pending = 0
    details = []

    for employee in active_employees:
        checked += 1

        if employee.total_learning_hours < employee.target_hours:
            continue  # not eligible yet

        newly_eligible += 1

        certificate, outcome = generate_certificate_for_employee(db, employee)

        if outcome == "created" and certificate:
            created += 1
            if certificate.email_sent:
                emails_sent += 1
            else:
                emails_pending += 1
            details.append({
                "employee_id": employee.id,
                "employee_name": employee.full_name,
                "certificate_id": certificate.certificate_id,
                "outcome": "created",
                "email_sent": certificate.email_sent,
            })
        elif outcome == "skipped_existing":
            skipped_existing += 1
            details.append({
                "employee_id": employee.id,
                "employee_name": employee.full_name,
                "outcome": "skipped_existing",
            })
        else:
            details.append({
                "employee_id": employee.id,
                "employee_name": employee.full_name,
                "outcome": outcome,
            })

    result = {
        "checked_employees": checked,
        "newly_eligible": newly_eligible,
        "certificates_created": created,
        "certificates_skipped_existing": skipped_existing,
        "emails_sent": emails_sent,
        "emails_pending": emails_pending,
        "details": details,
    }

    logger.info(
        "Automation run complete: checked=%s eligible=%s created=%s skipped=%s",
        checked, newly_eligible, created, skipped_existing,
    )
    return result
