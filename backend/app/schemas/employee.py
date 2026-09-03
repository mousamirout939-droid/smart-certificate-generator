from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    target_hours: float = Field(default=50, gt=0)
    password: str = Field(..., min_length=6, description="Initial login password for the employee user account")


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    target_hours: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    department: Optional[str]
    designation: Optional[str]
    joining_date: Optional[date]
    target_hours: float
    total_learning_hours: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeProgress(BaseModel):
    employee: EmployeeOut
    progress_percentage: float
    remaining_hours: float
    is_eligible: bool
