import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    joining_date = Column(Date, nullable=True)

    # Configurable per-employee target; falls back to global setting if null.
    target_hours = Column(Float, nullable=False, default=50)

    # Denormalized cache of learning hours, ALWAYS recalculated server-side
    # from learning_records - never trust a client-supplied value for this.
    total_learning_hours = Column(Float, nullable=False, default=0)

    status = Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="employee", uselist=False)
    learning_records = relationship("LearningRecord", back_populates="employee", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="employee", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="employee", cascade="all, delete-orphan")
