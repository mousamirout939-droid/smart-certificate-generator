from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings as env_settings
from app.models.user import User
from app.schemas.setting import SettingsOut, SettingsUpdate
from app.api.deps import require_admin
from app.services import settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    settings_service.ensure_defaults(db)
    return SettingsOut(
        certificate_target_hours=float(settings_service.get_setting(db, "CERTIFICATE_TARGET_HOURS")),
        automation_interval_minutes=int(settings_service.get_setting(db, "AUTOMATION_INTERVAL_MINUTES")),
        organization_name=settings_service.get_setting(db, "ORGANIZATION_NAME"),
        certificate_signature_name=settings_service.get_setting(db, "CERTIFICATE_SIGNATURE_NAME"),
        smtp_configured=env_settings.SMTP_CONFIGURED,
    )


@router.put("", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if payload.certificate_target_hours is not None:
        settings_service.set_setting(db, "CERTIFICATE_TARGET_HOURS", str(payload.certificate_target_hours))
    if payload.automation_interval_minutes is not None:
        settings_service.set_setting(db, "AUTOMATION_INTERVAL_MINUTES", str(payload.automation_interval_minutes))
    if payload.organization_name is not None:
        settings_service.set_setting(db, "ORGANIZATION_NAME", payload.organization_name)
    if payload.certificate_signature_name is not None:
        settings_service.set_setting(db, "CERTIFICATE_SIGNATURE_NAME", payload.certificate_signature_name)

    return get_settings(db=db, admin=admin)
