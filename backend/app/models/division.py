from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Division(Base):
    __tablename__ = "divisions"

    division_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # 7 divisions of Bangladesh

    districts = relationship("District", back_populates="division")
