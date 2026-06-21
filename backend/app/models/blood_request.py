import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.enums import UrgencyLevel, RequestStatus


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seeker_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id"), nullable=False)
    blood_group = Column(String(5), nullable=False)
    quantity_units = Column(Integer, nullable=False)
    urgency_level = Column(Enum(UrgencyLevel), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seeker = relationship("User", back_populates="blood_requests")
    district = relationship("District")
    matches = relationship("RequestMatch", back_populates="blood_request")
