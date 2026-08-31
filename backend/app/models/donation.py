"""
BloodReach BD — Donation Model
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, Text, Index, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class Donation(Base):
    __tablename__ = "donations"

    donation_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    match_id = Column(Uuid, ForeignKey("request_matches.match_id", ondelete="SET NULL"), unique=True)
    donor_id = Column(Uuid, ForeignKey("donors.donor_id", ondelete="CASCADE"), nullable=False)
    request_id = Column(Uuid, ForeignKey("blood_requests.request_id", ondelete="SET NULL"))
    hospital_id = Column(Uuid, ForeignKey("hospitals.hospital_id", ondelete="SET NULL"))
    blood_group = Column(String(5), nullable=False)
    units_donated = Column(Integer, nullable=False, default=1)
    donation_date = Column(Date, nullable=False, server_default=func.current_date())
    verified_by = Column(Uuid, ForeignKey("users.user_id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    match = relationship("RequestMatch", back_populates="donation")
    donor = relationship("Donor", back_populates="donations")
    request = relationship("BloodRequest", back_populates="donations")
    hospital = relationship("Hospital", back_populates="donations")
    verifier = relationship("User")

    __table_args__ = (
        Index("idx_donations_donor", "donor_id"),
        Index("idx_donations_hospital", "hospital_id"),
        Index("idx_donations_date", "donation_date"),
    )

    def __repr__(self):
        return f"<Donation(donation_id={self.donation_id}, donor_id={self.donor_id}, blood_group='{self.blood_group}', units={self.units_donated})>"