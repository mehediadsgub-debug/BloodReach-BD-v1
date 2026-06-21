import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.enums import MatchStatus


class RequestMatch(Base):
    """Junction table tracking donor responses to a blood request."""

    __tablename__ = "request_matches"

    match_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("blood_requests.request_id"), nullable=False)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("donors.donor_id"), nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.NOTIFIED)
    responded_at = Column(DateTime, nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)

    blood_request = relationship("BloodRequest", back_populates="matches")
    donor = relationship("Donor", back_populates="matches")
    donation = relationship("Donation", back_populates="match", uselist=False)
