import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id"), nullable=False)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False)
    contact_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District")
    inventory = relationship("HospitalInventory", back_populates="hospital")
