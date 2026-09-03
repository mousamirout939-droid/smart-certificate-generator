from sqlalchemy.orm import Session

from app.models.setting import Setting
from app.core.config import settings as env_settings

DEFAULTS = {
    "CERTIFICATE_TARGET_HOURS": str(env_settings.DEFAULT_TARGET_HOURS),
    "AUTOMATION_INTERVAL_MINUTES": str(env_settings.AUTOMATION_INTERVAL_MINUTES),
    "ORGANIZATION_NAME": env_settings.ORGANIZATION_NAME,
    "CERTIFICATE_SIGNATURE_NAME": env_settings.CERTIFICATE_SIGNATURE_NAME,
}


def get_setting(db: Session, key: str) -> str:
    row = db.query(Setting).filter(Setting.setting_key == key).first()
    if row:
        return row.setting_value
    return DEFAULTS.get(key, "")


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(Setting).filter(Setting.setting_key == key).first()
    if row:
        row.setting_value = value
        db.add(row)
    else:
        db.add(Setting(setting_key=key, setting_value=value))
    db.commit()


def get_default_target_hours(db: Session) -> float:
    return float(get_setting(db, "CERTIFICATE_TARGET_HOURS"))


def ensure_defaults(db: Session) -> None:
    for key, value in DEFAULTS.items():
        if not db.query(Setting).filter(Setting.setting_key == key).first():
            db.add(Setting(setting_key=key, setting_value=value))
    db.commit()
