"""
BloodReach BD — District Model
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.models.base import Base


class District(Base):
    __tablename__ = "districts"

    district_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    bn_name = Column(String(100))
    division_id = Column(Integer, ForeignKey("divisions.division_id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    division = relationship("Division", backref="districts")

    __table_args__ = (
        UniqueConstraint("name", "division_id", name="uq_district_name_division"),
        Index("idx_districts_division", "division_id"),
    )

    def __repr__(self):
        return f"<District(district_id={self.district_id}, name='{self.name}', division_id={self.division_id})>"