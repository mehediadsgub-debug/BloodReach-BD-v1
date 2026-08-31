"""
BloodReach BD — Blood Request Model
"""

import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Date, Text, Index, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class VerificationStatus(str, enum.Enum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FLAGGED_FRAUD = "FLAGGED_FRAUD"


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    request_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    seeker_id = Column(Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    blood_group = Column(String(5), nullable=False)
    units_needed = Column(Integer, nullable=False, default=1)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="SET NULL"))
    hospital_id = Column(Uuid, ForeignKey("hospitals.hospital_id", ondelete="SET NULL"))
    urgency_level = Column(Enum(UrgencyLevel, name="urgency_level"), nullable=False, default=UrgencyLevel.NORMAL)
    status = Column(Enum(RequestStatus, name="request_status"), nullable=False, default=RequestStatus.OPEN)
    
    # NID Verification & Anti-Fraud Fields
    nid_number = Column(String(30), nullable=True)
    nid_name = Column(String(150), nullable=True)
    nid_dob = Column(String(30), nullable=True)
    nid_image_url = Column(Text, nullable=True)
    hospital_name = Column(String(200), nullable=True)
    hospital_cabin = Column(String(100), nullable=True)
    verification_status = Column(Enum(VerificationStatus, name="verification_status"), nullable=False, default=VerificationStatus.PENDING_VERIFICATION)
    admin_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_id = Column(Uuid, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    patient_name = Column(String(150))
    patient_condition = Column(Text)
    required_by = Column(Date)
    contact_phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    seeker = relationship("User", foreign_keys=[seeker_id], back_populates="blood_requests")
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    district = relationship("District", backref="blood_requests")
    hospital = relationship("Hospital", back_populates="blood_requests")
    matches = relationship("RequestMatch", back_populates="request", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="request")

    __table_args__ = (
        Index("idx_requests_blood_group", "blood_group"),
        Index("idx_requests_district", "district_id"),
        Index("idx_requests_urgency", "urgency_level"),
        Index("idx_requests_status", "status"),
        Index("idx_requests_verification", "verification_status"),
        Index("idx_requests_seeker", "seeker_id"),
    )

    def __repr__(self):
        return f"<BloodRequest(request_id={self.request_id}, blood_group='{self.blood_group}', urgency='{self.urgency_level}', status='{self.status}')>"