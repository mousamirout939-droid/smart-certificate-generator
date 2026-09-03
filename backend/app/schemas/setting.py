from typing import Optional
from pydantic import BaseModel


class SettingsOut(BaseModel):
    certificate_target_hours: float
    automation_interval_minutes: int
    organization_name: str
    certificate_signature_name: str
    smtp_configured: bool


class SettingsUpdate(BaseModel):
    certificate_target_hours: Optional[float] = None
    automation_interval_minutes: Optional[int] = None
    organization_name: Optional[str] = None
    certificate_signature_name: Optional[str] = None
