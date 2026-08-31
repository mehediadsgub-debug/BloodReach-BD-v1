"""
BloodReach BD — Donor Model
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Date, Float, Index, CheckConstraint, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class Donor(Base):
    __tablename__ = "donors"

    donor_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    blood_group = Column(String(5), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    last_donation_date = Column(Date, nullable=True)
    total_donations = Column(Integer, nullable=False, default=0)
    weight_kg = Column(Float, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="donor_profile")
    matches = relationship("RequestMatch", back_populates="donor", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="donor")

    __table_args__ = (
        CheckConstraint("blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')", name="ck_donors_blood_group"),
        Index("idx_donors_blood_group", "blood_group"),
        Index("idx_donors_available", "is_available"),
        Index("idx_donors_user", "user_id"),
    )

    @property
    def division(self) -> str:
        if self.user and self.user.district and self.user.district.division:
            return self.user.district.division.name
        return None

    @property
    def district(self) -> str:
        if self.user and self.user.district:
            return self.user.district.name
        return None

    def __repr__(self):
        return f"<Donor(donor_id={self.donor_id}, blood_group='{self.blood_group}', available={self.is_available})>"