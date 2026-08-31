"""
BloodReach BD — Division Model
"""

from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Division(Base):
    __tablename__ = "divisions"

    division_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    bn_name = Column(String(100))

    def __repr__(self):
        return f"<Division(division_id={self.division_id}, name='{self.name}')>"