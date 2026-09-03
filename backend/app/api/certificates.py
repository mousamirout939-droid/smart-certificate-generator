import logging
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.certificate import Certificate
from app.models.employee import Employee
from app.models.user import User, UserRole
from app.schemas.certificate import CertificateOut, AutomationRunResult
from app.api.deps import get_current_user, require_admin
from app.services.automation_service import run_automation, generate_certificate_for_employee
from app.services.email_service import send_certificate_email

logger = logging.getLogger("app.certificates")

router = APIRouter(prefix="/api/certificates", tags=["certificates"])


@router.get("/verify/{certificate_id}")
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    certificate = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    employee = db.query(Employee).filter(Employee.id == certificate.employee_id).first()
    return {
        "valid": True,
        "certificate_id": certificate.certificate_id,
        "learner_name": employee.full_name if employee else None,
        "achievement_type": certificate.achievement_type,
        "issue_date": certificate.issue_date,
    }


def _assert_certificate_access(current_user: User, certificate: Certificate):
    """Employees may only access their own certificates - never another's."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.employee_id != certificate.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this certificate")


@router.get("", response_model=list[CertificateOut])
def list_certificates(
    certificate_id: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Certificate)

    if current_user.role != UserRole.ADMIN:
        # Employees can only ever see their own certificates.
        query = query.filter(Certificate.employee_id == current_user.employee_id)
    elif employee_id:
        query = query.filter(Certificate.employee_id == employee_id)

    if certificate_id:
        query = query.filter(Certificate.certificate_id.ilike(f"%{certificate_id}%"))

    return query.order_by(Certificate.id.desc()).all()


@router.get("/{cert_id}", response_model=CertificateOut)
def get_certificate(cert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    certificate = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    _assert_certificate_access(current_user, certificate)
    return certificate


@router.get("/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    certificate = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    _assert_certificate_access(current_user, certificate)

    pdf_path = Path(certificate.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Certificate file is missing on the server")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{certificate.certificate_id}.pdf",
    )


@router.post("/generate/{employee_id}", response_model=CertificateOut, status_code=status.HTTP_201_CREATED)
def generate_certificate_manually(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.total_learning_hours < employee.target_hours:
        raise HTTPException(status_code=400, detail="Employee has not yet reached their learning target")

    certificate, outcome = generate_certificate_for_employee(db, employee)
    if outcome == "skipped_existing":
        raise HTTPException(status_code=409, detail="A certificate for this achievement already exists")
    if certificate is None:
        raise HTTPException(status_code=500, detail=f"Certificate generation failed: {outcome}")

    return certificate


@router.post("/{cert_id}/resend", response_model=CertificateOut)
def resend_certificate_email(cert_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    certificate = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    employee = db.query(Employee).filter(Employee.id == certificate.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee for this certificate not found")

    result = send_certificate_email(
        to_email=employee.email,
        employee_name=employee.full_name,
        achieved_hours=certificate.achieved_hours,
        target_hours=certificate.target_hours,
        certificate_id=certificate.certificate_id,
        pdf_path=certificate.pdf_path,
    )

    from datetime import datetime
    certificate.email_sent = result.sent
    certificate.email_sent_at = datetime.utcnow() if result.sent else certificate.email_sent_at
    certificate.email_failure_reason = None if result.sent else result.reason
    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate
