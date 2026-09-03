from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut, EmployeeProgress
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=dict)
def list_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(Employee)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Employee.full_name.ilike(like))
            | (Employee.email.ilike(like))
            | (Employee.employee_code.ilike(like))
        )
    if department:
        query = query.filter(Employee.department == department)
    if status_filter:
        query = query.filter(Employee.status == status_filter)

    total = query.count()
    items = query.order_by(Employee.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [EmployeeOut.model_validate(e) for e in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="Employee code already exists")
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Employee email already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    employee = Employee(
        employee_code=payload.employee_code,
        full_name=payload.full_name,
        email=payload.email,
        department=payload.department,
        designation=payload.designation,
        joining_date=payload.joining_date,
        target_hours=payload.target_hours,
        total_learning_hours=0,
        status=EmployeeStatus.ACTIVE,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.EMPLOYEE,
        employee_id=employee.id,
        is_active=True,
    )
    db.add(user)
    db.commit()

    return employee


def _get_employee_or_404(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def _assert_employee_access(current_user: User, employee_id: int):
    """Employees may only access their own record; admins may access any."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.employee_id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this employee")


@router.get("/{employee_id}", response_model=EmployeeProgress)
def get_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _assert_employee_access(current_user, employee_id)
    employee = _get_employee_or_404(db, employee_id)

    target = employee.target_hours or 1
    progress_pct = min(100.0, round((employee.total_learning_hours / target) * 100, 2))
    remaining = max(0.0, round(employee.target_hours - employee.total_learning_hours, 2))
    is_eligible = employee.total_learning_hours >= employee.target_hours

    return EmployeeProgress(
        employee=EmployeeOut.model_validate(employee),
        progress_percentage=progress_pct,
        remaining_hours=remaining,
        is_eligible=is_eligible,
    )


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    employee = _get_employee_or_404(db, employee_id)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(employee, field, value)

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    employee = _get_employee_or_404(db, employee_id)
    employee.status = EmployeeStatus.INACTIVE
    db.add(employee)

    user = db.query(User).filter(User.employee_id == employee_id).first()
    if user:
        user.is_active = False
        db.add(user)

    db.commit()
    return None
