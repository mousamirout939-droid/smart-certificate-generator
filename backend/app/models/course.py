from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    duration_hours = Column(Float, nullable=False, default=0)
    price = Column(Float, nullable=False, default=0)
    payment_mode = Column(String(30), nullable=False, default="not_required")
    videos = Column(JSON, nullable=False, default=list)
    quiz_questions = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    learning_records = relationship("LearningRecord", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course")

    @property
    def quiz_required(self):
        return bool(self.quiz_questions)
