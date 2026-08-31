"""
BloodReach BD — Notification Service
Handles email (SMTP) and SMS notifications.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Notification, NotificationType, User, BloodRequest, RequestMatch, MatchStatus
from app.schemas import NotificationCreate
from app.core.config import settings


class NotificationService:
    """Notification service for email, SMS, and system notifications"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create a new notification, persist to DB, and broadcast via WebSocket"""
        db_notification = Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            related_request_id=notification.related_request_id
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)

        # Trigger real-time WebSocket push if client is connected
        try:
            from app.core.websocket_manager import ws_manager
            import asyncio
            payload = {
                "event": "NEW_NOTIFICATION",
                "notification": {
                    "notif_id": str(db_notification.notif_id),
                    "title": db_notification.title,
                    "message": db_notification.message,
                    "type": db_notification.type.value if hasattr(db_notification.type, 'value') else str(db_notification.type),
                    "created_at": db_notification.created_at.isoformat() if db_notification.created_at else None,
                    "related_request_id": str(db_notification.related_request_id) if db_notification.related_request_id else None
                }
            }
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.send_personal_message(str(notification.user_id), payload))
            except RuntimeError:
                # No active event loop in current thread
                pass
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"WebSocket push failed: {e}")

        return db_notification

    def send_system_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        related_request_id: Optional[UUID] = None
    ) -> Notification:
        """Send a system notification"""
        return self.create_notification(NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            type=NotificationType.SYSTEM,
            related_request_id=related_request_id
        ))

    def send_email_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        related_request_id: Optional[UUID] = None
    ) -> Notification:
        """Send an email notification"""
        notification = self.create_notification(NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            type=NotificationType.EMAIL,
            related_request_id=related_request_id
        ))
        return notification

    def send_sms_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        related_request_id: Optional[UUID] = None
    ) -> Notification:
        """Send an SMS notification"""
        notification = self.create_notification(NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            type=NotificationType.SMS,
            related_request_id=related_request_id
        ))

        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user and user.phone:
            from app.services.sms_service import default_sms_provider
            default_sms_provider.send_sms(user.phone, f"{title}: {message}")

        return notification

    def notify_donor_match(
        self,
        donor_user_id: UUID,
        request: BloodRequest,
        match_id: UUID
    ) -> Notification:
        """Notify donor about an admin-approved blood request match"""
        urgency_labels = {
            "CRITICAL": "🔴 CRITICAL",
            "HIGH": "🟠 HIGH",
            "NORMAL": "🟢 NORMAL",
            "LOW": "🟡 LOW"
        }
        urgency_label = urgency_labels.get(request.urgency_level.value, request.urgency_level.value)

        hospital_str = request.hospital_name or "Hospital"
        if request.hospital_cabin:
            hospital_str += f" (Cabin: {request.hospital_cabin})"

        invoice_no = f"INV-{str(request.request_id)[:8].upper()}"
        district_name = request.district.name if request.district else "Bangladesh"

        title = f"🩸 Admin Approved: {request.blood_group} Needed ({urgency_label})"
        message = (
            f"Admin has approved a blood request for {request.blood_group}. "
            f"Patient: {request.patient_name or 'Patient'} at {hospital_str}, {district_name}. "
            f"Seeker Phone: {request.contact_phone or 'See Dashboard'}. "
            f"Approval Invoice: {invoice_no}. Please respond in your dashboard."
        )

        notif = self.send_system_notification(donor_user_id, title, message, request.request_id)

        # For critical or high urgency, also dispatch immediate SMS alert to donor
        if request.urgency_level and request.urgency_level.value in ["CRITICAL", "HIGH", "URGENT"]:
            donor_user = self.db.query(User).filter(User.user_id == donor_user_id).first()
            if donor_user and donor_user.phone:
                self.notify_donor_match_sms(donor_user.phone, request)

        return notif

    def notify_donor_match_sms(
        self,
        phone_number: str,
        request: BloodRequest
    ) -> bool:
        """Send SMS to donor about critical match via SMS Provider"""
        urgency_labels = {
            "CRITICAL": "🔴 CRITICAL",
            "HIGH": "🟠 HIGH",
            "NORMAL": "🟢 NORMAL",
            "LOW": "🟡 LOW"
        }
        urgency_label = urgency_labels.get(request.urgency_level.value, request.urgency_level.value)

        message = (
            f"BloodReach BD: Urgent {request.blood_group} blood needed "
            f"({urgency_label}). Units: {request.units_needed}. "
            f"Location: {request.district.name if request.district else 'Unknown'}. "
            f"Please respond in app."
        )

        from app.services.sms_service import default_sms_provider
        return default_sms_provider.send_sms(phone_number, message)

    def notify_request_fulfilled(
        self,
        seeker_user_id: UUID,
        request: BloodRequest,
        donor_name: str
    ) -> Notification:
        """Notify seeker that their request has been fulfilled"""
        title = "Blood Request Fulfilled"
        message = (
            f"Your request for {request.blood_group} has been fulfilled by {donor_name}. "
            f"Please coordinate with the donor/hospital for collection."
        )
        return self.send_system_notification(seeker_user_id, title, message, request.request_id)

    def notify_request_cancelled(
        self,
        seeker_user_id: UUID,
        request: BloodRequest
    ) -> Notification:
        """Notify seeker that their request was cancelled"""
        title = "Blood Request Cancelled"
        message = f"Your request for {request.blood_group} has been cancelled."
        return self.send_system_notification(seeker_user_id, title, message, request.request_id)

    def notify_low_stock(
        self,
        hospital_admin_user_id: UUID,
        blood_group: str,
        current_units: int,
        threshold: int
    ) -> Notification:
        """Notify hospital admin about low stock"""
        title = f"Low Stock Alert: {blood_group}"
        message = (
            f"Stock for {blood_group} has fallen to {current_units} units "
            f"(threshold: {threshold}). Please update inventory."
        )
        return self.send_system_notification(hospital_admin_user_id, title, message)

    def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.notif_id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user"""
        result = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({"is_read": True})
        self.db.commit()
        return result