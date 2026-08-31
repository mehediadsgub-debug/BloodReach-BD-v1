"""
BloodReach BD — Notification Routes
User alerts, in-app notifications, and mark-as-read endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User, Notification
from app.schemas import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve notifications for the authenticated user"""
    service = NotificationService(db)
    return service.get_user_notifications(current_user.user_id, unread_only=unread_only, limit=limit)


@router.patch("/{notif_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notif_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    service = NotificationService(db)
    notif = service.mark_as_read(notif_id, current_user.user_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notif


@router.post("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the authenticated user"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.user_id)
    return {"message": "All notifications marked as read", "updated_count": count}
