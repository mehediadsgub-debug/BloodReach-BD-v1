"""
BloodReach BD — User Model
"""

import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer, Index, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.base import Base


class UserRole(str, enum.Enum):
    DONOR = "DONOR"
    SEEKER = "SEEKER"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    SUPERADMIN = "SUPERADMIN"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="SET NULL"))
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    profile_pic_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    district = relationship("District", backref="users")
    donor_profile = relationship("Donor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    hospital_admin = relationship("Hospital", back_populates="admin_user", uselist=False)
    blood_requests = relationship("BloodRequest", back_populates="seeker", cascade="all, delete-orphan", foreign_keys="[BloodRequest.seeker_id]")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_role", "role"),
        Index("idx_users_district", "district_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_active", "is_active"),
    )

    @property
    def name(self) -> str:
        return self.full_name

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email='{self.email}', role='{self.role}')>"