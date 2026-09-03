import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User, UserRole
from app.models.employee import Employee, EmployeeStatus
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, CurrentUser
from app.api.deps import get_current_user

logger = logging.getLogger("app.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    if len(payload.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=422, detail="Full name is required")

    employee = Employee(
        employee_code=f"LEARNER-{db.query(Employee).count() + 1:04d}",
        full_name=full_name,
        email=payload.email,
        status=EmployeeStatus.ACTIVE,
    )
    db.add(employee)
    db.flush()
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.EMPLOYEE,
        employee_id=employee.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token({"sub": str(user.id), "role": user.role.value}))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        logger.info("Failed login attempt for email=%s", payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    logger.info("Successful login for user_id=%s role=%s", user.id, user.role)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: User = Depends(get_current_user)):
    return CurrentUser(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role.value,
        employee_id=current_user.employee_id,
        is_active=current_user.is_active,
    )
