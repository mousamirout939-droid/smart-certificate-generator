import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.automation_service import run_automation

logger = logging.getLogger("app.scheduler")

_scheduler: BackgroundScheduler | None = None
_last_run_info = {"last_run_at": None, "summary": None}


def get_last_run_info() -> dict:
    return _last_run_info


def _scheduled_automation_job():
    db = SessionLocal()
    try:
        result = run_automation(db)
        _last_run_info["last_run_at"] = datetime.utcnow().isoformat()
        _last_run_info["summary"] = (
            f"checked={result['checked_employees']} "
            f"created={result['certificates_created']} "
            f"skipped={result['certificates_skipped_existing']}"
        )
        logger.info("Scheduled automation run: %s", _last_run_info["summary"])
    except Exception as e:  # noqa: BLE001 - scheduler jobs must never crash the process
        logger.error("Scheduled automation run failed: %s", e)
    finally:
        db.close()


def start_scheduler():
    """
    Starts the background scheduler exactly once. Guards against duplicate
    instances that uvicorn's --reload can otherwise spawn (each reload
    forks a new process, but within a single process this is idempotent).
    """
    global _scheduler

    if not settings.ENABLE_AUTOMATION:
        logger.info("Automation is disabled via ENABLE_AUTOMATION=false; scheduler not started")
        return

    if _scheduler is not None and _scheduler.running:
        logger.info("Scheduler already running; skipping duplicate start")
        return

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _scheduled_automation_job,
        "interval",
        minutes=settings.AUTOMATION_INTERVAL_MINUTES,
        id="learning_target_automation",
        replace_existing=True,
        next_run_time=None,  # first run happens after one interval, not immediately
    )
    _scheduler.start()
    logger.info("Scheduler started: automation runs every %s minutes", settings.AUTOMATION_INTERVAL_MINUTES)


def shutdown_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler shut down")
