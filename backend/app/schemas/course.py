from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    duration_hours: float = Field(default=0, ge=0)
    price: float = Field(default=0, ge=0)
    payment_mode: str = Field(default="not_required", min_length=1, max_length=30)
    videos: list[dict[str, Any]] = Field(default_factory=list)
    quiz_questions: list[dict[str, Any]] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_hours: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    payment_mode: Optional[str] = Field(default=None, min_length=1, max_length=30)
    videos: Optional[list[dict[str, Any]]] = None
    quiz_questions: Optional[list[dict[str, Any]]] = None
    is_active: Optional[bool] = None


class CourseOut(BaseModel):
    id: int
    course_code: str
    title: str
    description: Optional[str]
    category: Optional[str]
    duration_hours: float
    price: float
    payment_mode: str
    videos: list[dict[str, Any]]
    quiz_required: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuizQuestionOut(BaseModel):
    id: str
    question: str
    options: list[str]


class QuizSubmission(BaseModel):
    answers: dict[str, str]


class QuizResult(BaseModel):
    score: float
    passed: bool
    correct_answers: int
    total_questions: int
