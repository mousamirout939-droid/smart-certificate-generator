import os
import sys
import tempfile

import pytest

# Ensure a clean, isolated test database before importing the app.
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.close(_test_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ["ENABLE_AUTOMATION"] = "false"  # don't start the background scheduler during tests
os.environ["SMTP_HOST"] = ""  # force "email pending" path so tests are deterministic/offline

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.core.database import SessionLocal, init_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.models.employee import Employee, EmployeeStatus  # noqa: E402
from app.models.course import Course  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db():
    """Reset all tables before every test for full isolation."""
    init_db()
    db = SessionLocal()
    from app.models.certificate import Certificate
    from app.models.learning_record import LearningRecord
    from app.models.enrollment import Enrollment
    from app.models.setting import Setting

    db.query(Certificate).delete()
    db.query(LearningRecord).delete()
    db.query(Enrollment).delete()
    db.query(Course).delete()
    db.query(User).delete()
    db.query(Employee).delete()
    db.query(Setting).delete()
    db.commit()
    db.close()
    yield


def create_admin(db, email="admin@example.com", password="Password123!"):
    admin = User(email=email, password_hash=hash_password(password), role=UserRole.ADMIN, is_active=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def create_employee(db, code="EMP-100", name="Test Employee", email="test.employee@example.com",
                     target_hours=50, password="Password123!", total_hours=0):
    employee = Employee(
        employee_code=code, full_name=name, email=email, department="Engineering",
        target_hours=target_hours, total_learning_hours=total_hours, status=EmployeeStatus.ACTIVE,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    user = User(email=email, password_hash=hash_password(password), role=UserRole.EMPLOYEE,
                employee_id=employee.id, is_active=True)
    db.add(user)
    db.commit()
    return employee


def login(client, email, password="Password123!"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()
