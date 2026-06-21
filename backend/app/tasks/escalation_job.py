"""APScheduler cron job: escalate unmatched critical requests after 30 minutes."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.urgency_service import escalate_unmatched_critical_requests
from app.database import SessionLocal

scheduler = BackgroundScheduler()


def _job():
    db = SessionLocal()
    try:
        escalate_unmatched_critical_requests(db)
    finally:
        db.close()


def start_escalation_job():
    scheduler.add_job(_job, "interval", minutes=5, id="escalation_job")
    scheduler.start()
