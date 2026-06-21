from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class District(Base):
    __tablename__ = "districts"

    district_id = Column(Integer, primary_key=True)
    division_id = Column(Integer, ForeignKey("divisions.division_id"), nullable=False)
    name = Column(String(100), unique=True, nullable=False)  # 64 districts of Bangladesh
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)

    division = relationship("Division", back_populates="districts")
    users = relationship("User", back_populates="district")
