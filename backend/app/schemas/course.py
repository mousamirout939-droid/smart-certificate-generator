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
    videos: list[dict[str, Any]] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_hours: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    videos: Optional[list[dict[str, Any]]] = None
    is_active: Optional[bool] = None


class CourseOut(BaseModel):
    id: int
    course_code: str
    title: str
    description: Optional[str]
    category: Optional[str]
    duration_hours: float
    price: float
    videos: list[dict[str, Any]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
