"""
BloodReach BD — Audit Log Model
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Index, JSON, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_id = Column(Uuid, ForeignKey("users.user_id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    target_table = Column(String(100))
    target_id = Column(Uuid)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    actor = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_actor", "actor_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_time", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog(log_id={self.log_id}, actor_id={self.actor_id}, action='{self.action}')>"