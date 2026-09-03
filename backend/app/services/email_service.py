"""
Email delivery service.

Design goals (per spec):
- SMTP credentials come only from environment variables, never hardcoded.
- If SMTP is not configured, certificate generation must still succeed;
  we simply report that email is "pending" and log why.
- If sending fails for any other reason, we never raise up into a request
  that would delete/roll back the certificate - the caller records the
  failure status and the admin can retry.
"""
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger("app.email")


@dataclass
class EmailResult:
    sent: bool
    reason: str = ""


def send_certificate_email(
    *,
    to_email: str,
    employee_name: str,
    achieved_hours: float,
    target_hours: float,
    certificate_id: str,
    pdf_path: str,
) -> EmailResult:
    if not settings.SMTP_CONFIGURED:
        reason = "SMTP not configured (missing SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/SMTP_FROM)"
        logger.warning("Email not sent for certificate %s: %s", certificate_id, reason)
        return EmailResult(sent=False, reason=reason)

    subject = "Your Learning Achievement Certificate"
    body = (
        f"Hello {employee_name},\n\n"
        f"Congratulations on reaching your learning target.\n\n"
        f"Learning hours completed: {achieved_hours:g}\n"
        f"Target: {target_hours:g}\n"
        f"Certificate ID: {certificate_id}\n\n"
        f"Your certificate is attached to this email.\n\n"
        f"Regards,\n"
        f"Learning & Development Team"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(body)

    pdf_file = Path(pdf_path)
    try:
        with open(pdf_file, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=pdf_file.name,
            )
    except OSError as e:
        reason = f"Could not read generated PDF for attachment: {e}"
        logger.error("Email attachment failure for certificate %s: %s", certificate_id, reason)
        return EmailResult(sent=False, reason=reason)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Certificate email sent for %s to %s", certificate_id, to_email)
        return EmailResult(sent=True)
    except Exception as e:  # noqa: BLE001 - we deliberately never let email failures crash the app
        reason = f"SMTP send failed: {e}"
        logger.error("Email send failure for certificate %s: %s", certificate_id, reason)
        return EmailResult(sent=False, reason=reason)
