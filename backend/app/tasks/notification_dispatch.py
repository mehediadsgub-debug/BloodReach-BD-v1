"""FastAPI BackgroundTasks worker for asynchronous notification dispatch."""

from app.services.notification_service import send_email, send_sms
from app.utils.enums import NotificationType


def dispatch_notification(notification_type: NotificationType, recipient: str, message: str):
    if notification_type == NotificationType.EMAIL:
        send_email(recipient, "Blood Reach BD Notification", message)
    elif notification_type == NotificationType.SMS:
        send_sms(recipient, message)
    # SYSTEM notifications are written directly to the notifications table, no dispatch needed.
