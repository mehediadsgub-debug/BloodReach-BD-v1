"""
BloodReach BD — Scheduler Service
APScheduler background jobs for urgency escalation and other periodic tasks.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.escalation_service import run_escalation_job
import os
import time
import tempfile
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# Cross-worker lock file
LOCK_FILE = os.path.join(tempfile.gettempdir(), "bloodreach_scheduler.lock")


def acquire_worker_lock(job_name: str, lock_ttl_seconds: int = 120) -> bool:
    """Ensure only one worker executes a scheduled job within TTL"""
    lock_path = f"{LOCK_FILE}_{job_name}"
    now = time.time()
    try:
        if os.path.exists(lock_path):
            with open(lock_path, "r") as f:
                content = f.read().strip()
                if content:
                    last_time = float(content)
                    if now - last_time < lock_ttl_seconds:
                        return False  # Locked by another worker

        with open(lock_path, "w") as f:
            f.write(str(now))
        return True
    except Exception:
        return True  # Fallback to execution if filesystem locking fails


def escalation_job():
    """Wrapper to run escalation job with database session and worker lock"""
    if not acquire_worker_lock("escalation", lock_ttl_seconds=180):
        logger.debug("Escalation job skipped (locked by another worker)")
        return

    db = SessionLocal()
    try:
        result = run_escalation_job(db)
        logger.info(f"Escalation job completed: {result}")
    except Exception as e:
        logger.error(f"Escalation job failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Add escalation job - runs every 5 minutes
    scheduler.add_job(
        escalation_job,
        trigger=IntervalTrigger(minutes=5),
        id="escalation_check",
        name="Check and escalate critical blood requests",
        replace_existing=True
    )

    # Add low stock check job - runs every 30 minutes
    scheduler.add_job(
        check_low_stock_job,
        trigger=IntervalTrigger(minutes=30),
        id="low_stock_check",
        name="Check hospital inventory for low stock",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with jobs: escalation_check (5min), low_stock_check (30min)")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")


def check_low_stock_job():
    """Check hospital inventory for low stock and notify admins"""
    db = SessionLocal()
    try:
        from app.models import HospitalInventory, Hospital, User, UserRole
        from app.services.notification_service import NotificationService

        notification_service = NotificationService(db)

        # Find inventory below threshold
        low_stock_items = db.query(HospitalInventory).filter(
            HospitalInventory.units_available <= HospitalInventory.low_stock_alert
        ).all()

        for item in low_stock_items:
            hospital = db.query(Hospital).filter(Hospital.hospital_id == item.hospital_id).first()
            if not hospital or not hospital.admin_user_id:
                continue

            notification_service.notify_low_stock(
                hospital_admin_user_id=hospital.admin_user_id,
                blood_group=item.blood_group,
                current_units=item.units_available,
                threshold=item.low_stock_alert
            )

        logger.info(f"Low stock check completed: {len(low_stock_items)} alerts sent")
    except Exception as e:
        logger.error(f"Low stock check failed: {e}")
    finally:
        db.close()