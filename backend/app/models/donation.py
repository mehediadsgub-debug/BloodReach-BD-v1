import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Donation(Base):
    """Created automatically when a RequestMatch status becomes FULFILLED."""

    __tablename__ = "donations"

    donation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("request_matches.match_id"), unique=True, nullable=False)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("donors.donor_id"), nullable=False)
    request_id = Column(UUID(as_uuid=True), ForeignKey("blood_requests.request_id"), nullable=False)
    donated_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("RequestMatch", back_populates="donation")
    donor = relationship("Donor", back_populates="donations")
