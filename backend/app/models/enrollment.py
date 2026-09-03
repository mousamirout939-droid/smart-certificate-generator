import enum
from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.ACTIVE)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.NOT_REQUIRED)
    amount = Column(Float, nullable=False, default=0)
    provider_reference = Column(String(255), nullable=True)
    watched_video_ids = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (UniqueConstraint("employee_id", "course_id", name="uq_enrollment_employee_course"),)