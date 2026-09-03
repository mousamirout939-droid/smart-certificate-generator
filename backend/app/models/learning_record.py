import enum
from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LearningRecord(Base):
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    learning_hours = Column(Float, nullable=False)
    completion_percentage = Column(Float, nullable=False, default=0)
    completion_date = Column(Date, nullable=True)
    status = Column(Enum(LearningStatus), nullable=False, default=LearningStatus.IN_PROGRESS)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="learning_records")
    course = relationship("Course", back_populates="learning_records")
