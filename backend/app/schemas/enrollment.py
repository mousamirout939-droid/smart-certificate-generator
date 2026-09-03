from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    status: str
    payment_status: str
    amount: float
    provider_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    watched_video_ids: list[str] = []

    class Config:
        from_attributes = True


class EnrollmentActionOut(BaseModel):
    enrolled: bool
    checkout_required: bool = False
    message: str
    enrollment: Optional[EnrollmentOut] = None