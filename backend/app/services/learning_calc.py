"""
Single source of truth for computing an employee's total learning hours.

Never trust a frontend-provided total. Always derive it from the
learning_records table.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.learning_record import LearningRecord
from app.models.employee import Employee


def recalculate_employee_hours(db: Session, employee_id: int) -> float:
    total = (
        db.query(func.coalesce(func.sum(LearningRecord.learning_hours), 0.0))
        .filter(LearningRecord.employee_id == employee_id)
        .scalar()
    )
    total = float(total or 0.0)

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.total_learning_hours = total
        db.add(employee)
        db.commit()

    return total
