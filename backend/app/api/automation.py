from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.certificate import AutomationRunResult
from app.api.deps import require_admin
from app.services.automation_service import run_automation
from app.scheduler.jobs import get_last_run_info

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.post("/run", response_model=AutomationRunResult)
def trigger_automation(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """'Run Automation Now' button - lets admins test without waiting for the scheduler."""
    result = run_automation(db)
    return result


@router.get("/status")
def automation_status(admin: User = Depends(require_admin)):
    last_run = get_last_run_info()
    return {
        "enabled": settings.ENABLE_AUTOMATION,
        "interval_minutes": settings.AUTOMATION_INTERVAL_MINUTES,
        "last_run_at": last_run.get("last_run_at"),
        "last_run_summary": last_run.get("summary"),
    }
