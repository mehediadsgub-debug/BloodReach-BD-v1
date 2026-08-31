"""
BloodReach BD — Hospital Model
"""

import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer, Index, Text, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="SET NULL"))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    admin_user_id = Column(Uuid, ForeignKey("users.user_id", ondelete="SET NULL"), unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    district = relationship("District", backref="hospitals")
    admin_user = relationship("User", back_populates="hospital_admin")
    inventory = relationship("HospitalInventory", back_populates="hospital", cascade="all, delete-orphan")
    blood_requests = relationship("BloodRequest", back_populates="hospital")
    donations = relationship("Donation", back_populates="hospital")

    __table_args__ = (
        Index("idx_hospitals_district", "district_id"),
        Index("idx_hospitals_active", "is_active"),
    )

    def __repr__(self):
        return f"<Hospital(hospital_id={self.hospital_id}, name='{self.name}')>"