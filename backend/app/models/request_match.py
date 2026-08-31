"""
BloodReach BD — Request Match Model
"""

import enum
from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, Text, UniqueConstraint, Index, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class MatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class RequestMatch(Base):
    __tablename__ = "request_matches"

    match_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    request_id = Column(Uuid, ForeignKey("blood_requests.request_id", ondelete="CASCADE"), nullable=False)
    donor_id = Column(Uuid, ForeignKey("donors.donor_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(MatchStatus, name="match_status"), nullable=False, default=MatchStatus.PENDING)
    matched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True))
    notes = Column(Text)

    # Relationships
    request = relationship("BloodRequest", back_populates="matches")
    donor = relationship("Donor", back_populates="matches")
    donation = relationship("Donation", back_populates="match", uselist=False)

    __table_args__ = (
        UniqueConstraint("request_id", "donor_id", name="uq_match_request_donor"),
        Index("idx_matches_request", "request_id"),
        Index("idx_matches_donor", "donor_id"),
        Index("idx_matches_status", "status"),
    )

    def __repr__(self):
        return f"<RequestMatch(match_id={self.match_id}, request_id={self.request_id}, donor_id={self.donor_id}, status='{self.status}')>"