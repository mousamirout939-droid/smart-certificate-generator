from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LearningRecordCreate(BaseModel):
    employee_id: int
    course_id: int
    learning_hours: float = Field(..., gt=0)
    completion_percentage: float = Field(..., ge=0, le=100)
    completion_date: Optional[date] = None

    @field_validator("learning_hours")
    @classmethod
    def hours_positive(cls, v):
        if v <= 0:
            raise ValueError("learning_hours must be greater than 0")
        return v


class LearnerLearningRecordCreate(BaseModel):
    course_id: int
    learning_hours: float = Field(..., gt=0)
    completion_percentage: float = Field(..., ge=0, le=100)
    completion_date: Optional[date] = None

    @field_validator("learning_hours")
    @classmethod
    def hours_positive(cls, v):
        if v <= 0:
            raise ValueError("learning_hours must be greater than 0")
        return v


class LearningRecordOut(BaseModel):
    id: int
    employee_id: int
    course_id: int
    learning_hours: float
    completion_percentage: float
    completion_date: Optional[date]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
