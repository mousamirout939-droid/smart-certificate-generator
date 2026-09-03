from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    achievement_type = Column(String(50), nullable=False, default="LEARNING_TARGET")
    target_hours = Column(Float, nullable=False)
    achieved_hours = Column(Float, nullable=False)

    issue_date = Column(Date, nullable=False, default=datetime.utcnow)
    pdf_path = Column(String(500), nullable=False)

    email_sent = Column(Boolean, nullable=False, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    email_failure_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")

    __table_args__ = (
        # Database-level duplicate prevention: an employee can only have ONE
        # certificate per (achievement_type, target_hours) combination.
        UniqueConstraint(
            "employee_id", "achievement_type", "target_hours",
            name="uq_certificate_employee_achievement_target",
        ),
    )
