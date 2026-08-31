"""
BloodReach BD — Hospital Inventory Model
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class HospitalInventory(Base):
    __tablename__ = "hospital_inventory"

    inv_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    hospital_id = Column(Uuid, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False)
    blood_group = Column(String(5), nullable=False)
    units_available = Column(Integer, nullable=False, default=0)
    low_stock_alert = Column(Integer, nullable=False, default=5)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="inventory")

    __table_args__ = (
        UniqueConstraint("hospital_id", "blood_group", name="uq_inventory_hospital_blood_group"),
        Index("idx_inventory_hospital", "hospital_id"),
        Index("idx_inventory_blood_group", "blood_group"),
    )

    def __repr__(self):
        return f"<HospitalInventory(hospital_id={self.hospital_id}, blood_group='{self.blood_group}', units={self.units_available})>"