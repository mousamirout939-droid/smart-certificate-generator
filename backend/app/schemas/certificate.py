from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class CertificateOut(BaseModel):
    id: int
    certificate_id: str
    employee_id: int
    course_id: Optional[int]
    achievement_type: str
    target_hours: float
    achieved_hours: float
    issue_date: date
    email_sent: bool
    email_sent_at: Optional[datetime]
    email_failure_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AutomationRunResult(BaseModel):
    checked_employees: int
    newly_eligible: int
    certificates_created: int
    certificates_skipped_existing: int
    emails_sent: int
    emails_pending: int
    details: list
