import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Donor(Base):
    __tablename__ = "donors"

    donor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False)
    blood_group = Column(String(5), nullable=False)
    is_available = Column(Boolean, default=True)
    last_donated = Column(Date, nullable=True)
    total_donations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="donor")
    matches = relationship("RequestMatch", back_populates="donor")
    donations = relationship("Donation", back_populates="donor")
