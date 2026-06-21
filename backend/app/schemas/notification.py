import uuid
from datetime import datetime

from pydantic import BaseModel

from app.utils.enums import NotificationType


class NotificationOut(BaseModel):
    notif_id: uuid.UUID
    recipient_id: uuid.UUID
    type: NotificationType
    message: str
    is_read: bool
    sent_at: datetime

    class Config:
        from_attributes = True
