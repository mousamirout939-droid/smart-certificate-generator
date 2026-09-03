from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.employee import Employee, EmployeeStatus
from app.models.certificate import Certificate
from app.models.user import User, UserRole
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        return _admin_dashboard(db)
    return _employee_dashboard(db, current_user)


def _admin_dashboard(db: Session):
    employees = db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE).all()

    total_employees = len(employees)
    total_hours = sum(e.total_learning_hours for e in employees)
    eligible_employees = [e for e in employees if e.total_learning_hours >= e.target_hours]
    non_eligible_count = total_employees - len(eligible_employees)

    total_certificates = db.query(func.count(Certificate.id)).scalar() or 0
    pending_email = db.query(func.count(Certificate.id)).filter(Certificate.email_sent == False).scalar() or 0  # noqa: E712

    # Department stats
    dept_stats = {}
    for e in employees:
        dept = e.department or "Unassigned"
        dept_stats.setdefault(dept, {"employees": 0, "total_hours": 0.0})
        dept_stats[dept]["employees"] += 1
        dept_stats[dept]["total_hours"] += e.total_learning_hours

    recent_certificates = (
        db.query(Certificate).order_by(Certificate.id.desc()).limit(5).all()
    )

    return {
        "cards": {
            "total_employees": total_employees,
            "total_learning_hours": round(total_hours, 2),
            "employees_eligible": len(eligible_employees),
            "certificates_generated": total_certificates,
            "certificates_pending_email": pending_email,
        },
        "charts": {
            "eligible_vs_non_eligible": {
                "eligible": len(eligible_employees),
                "non_eligible": non_eligible_count,
            },
            "department_stats": [
                {"department": dept, **stats} for dept, stats in dept_stats.items()
            ],
            "learning_progress": [
                {"employee": e.full_name, "hours": e.total_learning_hours, "target": e.target_hours}
                for e in employees
            ],
        },
        "recent_activity": {
            "newly_eligible": [
                {"id": e.id, "name": e.full_name, "hours": e.total_learning_hours, "target": e.target_hours}
                for e in eligible_employees[:5]
            ],
            "recent_certificates": [
                {
                    "certificate_id": c.certificate_id,
                    "employee_id": c.employee_id,
                    "issue_date": str(c.issue_date),
                    "email_sent": c.email_sent,
                }
                for c in recent_certificates
            ],
        },
    }


def _employee_dashboard(db: Session, current_user: User):
    employee = db.query(Employee).filter(Employee.id == current_user.employee_id).first()
    if not employee:
        return {"error": "Employee record not found"}

    target = employee.target_hours or 1
    progress_pct = min(100.0, round((employee.total_learning_hours / target) * 100, 2))
    remaining = max(0.0, round(employee.target_hours - employee.total_learning_hours, 2))
    is_eligible = employee.total_learning_hours >= employee.target_hours

    certificate = (
        db.query(Certificate)
        .filter(Certificate.employee_id == employee.id)
        .order_by(Certificate.id.desc())
        .first()
    )

    return {
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "department": employee.department,
            "target_hours": employee.target_hours,
            "total_learning_hours": employee.total_learning_hours,
        },
        "progress_percentage": progress_pct,
        "remaining_hours": remaining,
        "is_eligible": is_eligible,
        "certificate": {
            "certificate_id": certificate.certificate_id,
            "issue_date": str(certificate.issue_date),
            "id": certificate.id,
        } if certificate else None,
    }
