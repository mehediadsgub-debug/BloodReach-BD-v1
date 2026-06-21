from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.notification import NotificationOut

router = APIRouter()


@router.get("/", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    raise NotImplementedError


@router.patch("/{notif_id}/read", response_model=NotificationOut)
def mark_as_read(notif_id: str, db: Session = Depends(get_db)):
    # TODO: Notification.markAsRead()
    raise NotImplementedError
