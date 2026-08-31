"""
BloodReach BD — Notification Model
"""

import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, DateTime, Text, Index, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class NotificationType(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    SYSTEM = "SYSTEM"
    PUSH = "PUSH"


class Notification(Base):
    __tablename__ = "notifications"

    notif_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType, name="notification_type"), nullable=False, default=NotificationType.SYSTEM)
    is_read = Column(Boolean, nullable=False, default=False)
    related_request_id = Column(Uuid, ForeignKey("blood_requests.request_id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
    related_request = relationship("BloodRequest")

    __table_args__ = (
        Index("idx_notif_user", "user_id"),
        Index("idx_notif_unread", "user_id", "is_read"),
    )

    def __repr__(self):
        return f"<Notification(notif_id={self.notif_id}, user_id={self.user_id}, type='{self.type}', read={self.is_read})>"