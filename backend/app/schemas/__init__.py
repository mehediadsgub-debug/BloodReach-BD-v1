"""
BloodReach BD — Pydantic Schemas
Request/Response validation schemas.
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models import UserRole, UrgencyLevel, RequestStatus, VerificationStatus, MatchStatus, NotificationType


# ── Base schemas ──────────────────────────────────────────────
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


from pydantic import field_validator

# ── Auth schemas ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in ["ADMIN", "SUPERADMIN"]:
                return UserRole.SUPERADMIN
            if v_upper in ["HOSPITAL", "HOSPITAL_ADMIN"]:
                return UserRole.HOSPITAL_ADMIN
            if v_upper == "DONOR":
                return UserRole.DONOR
            if v_upper == "SEEKER":
                return UserRole.SEEKER
        return v


import re

class RegisterRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{7,15}$")
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole
    blood_group: Optional[str] = Field(None, pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    division_id: Optional[int] = None
    district_id: Optional[int] = None
    # Frontend sends location by NAME (not id) — resolved to ids in the route
    division: Optional[str] = None
    district: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return None
        return v.strip().lower() if isinstance(v, str) else v

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in ["ADMIN", "SUPERADMIN"]:
                return UserRole.SUPERADMIN
            if v_upper in ["HOSPITAL", "HOSPITAL_ADMIN"]:
                return UserRole.HOSPITAL_ADMIN
            if v_upper == "DONOR":
                return UserRole.DONOR
            if v_upper == "SEEKER":
                return UserRole.SEEKER
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, str):
            cleaned = re.sub(r"[\s\-\(\)]", "", v.strip())
            return cleaned if cleaned else None
        return v

    @field_validator("blood_group", mode="before")
    @classmethod
    def normalize_blood_group(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, str):
            cleaned = v.replace(" ", "+").strip().upper()
            return cleaned if cleaned else None
        return v


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: UUID
    full_name: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Division/District schemas ─────────────────────────────────
class DivisionResponse(BaseSchema):
    division_id: int
    name: str
    bn_name: Optional[str] = None


class DistrictResponse(BaseSchema):
    district_id: int
    name: str
    bn_name: Optional[str] = None
    division_id: int
    division: Optional[DivisionResponse] = None


# ── User schemas ──────────────────────────────────────────────
class UserBase(BaseSchema):
    full_name: str
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    district_id: Optional[int] = None
    district: Optional[DistrictResponse] = None
    is_active: bool
    is_verified: bool
    profile_pic_url: Optional[str] = None


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole
    district_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    district_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(UserResponse):
    donor_profile: Optional["DonorResponse"] = None
    hospital_admin: Optional["HospitalResponse"] = None


# ── Donor schemas ─────────────────────────────────────────────
class DonorBase(BaseSchema):
    blood_group: str
    is_available: bool
    division: Optional[str] = None
    district: Optional[str] = None
    last_donation_date: Optional[date]
    total_donations: int
    weight_kg: Optional[float]
    date_of_birth: Optional[date]
    emergency_contact: Optional[str]


class DonorCreate(BaseModel):
    blood_group: str = Field(..., pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    weight_kg: Optional[float] = Field(None, ge=30, le=200)
    date_of_birth: Optional[date] = None
    emergency_contact: Optional[str] = Field(None, max_length=20)


class DonorUpdate(BaseModel):
    blood_group: Optional[str] = Field(None, pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    is_available: Optional[bool] = None
    weight_kg: Optional[float] = Field(None, ge=30, le=200)
    date_of_birth: Optional[date] = None
    emergency_contact: Optional[str] = Field(None, max_length=20)


class DonorResponse(DonorBase):
    donor_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class DonorSearchResult(BaseSchema):
    donor_id: UUID
    full_name: str
    blood_group: str
    is_available: bool
    division: Optional[str] = None
    district: Optional[str] = None
    last_donation_date: Optional[date] = None
    total_donations: int = 0
    phone: Optional[str] = None
    is_phone_unlocked: bool = False


class UserStatusUpdate(BaseModel):
    is_active: bool


# ── Profile Update schemas ────────────────────────────────────
class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    is_available: Optional[bool] = None


# ── Hospital schemas ──────────────────────────────────────────
class HospitalBase(BaseSchema):
    name: str
    address: Optional[str]
    district_id: Optional[int]
    contact_phone: Optional[str]
    contact_email: Optional[EmailStr]
    is_active: bool


class HospitalCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    address: Optional[str] = None
    district_id: Optional[int] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class HospitalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = None
    district_id: Optional[int] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class HospitalResponse(HospitalBase):
    hospital_id: UUID
    admin_user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


# ── Hospital Inventory schemas ────────────────────────────────
class InventoryBase(BaseSchema):
    blood_group: str
    units_available: int
    low_stock_alert: int


class InventoryCreate(BaseModel):
    blood_group: str = Field(..., pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    units_available: int = Field(..., ge=0, le=9999)
    low_stock_alert: int = Field(5, ge=0, le=100)


class InventoryUpdate(BaseModel):
    units_available: Optional[int] = Field(None, ge=0, le=9999)
    low_stock_alert: Optional[int] = Field(None, ge=0, le=100)


class InventoryResponse(InventoryBase):
    inv_id: UUID
    hospital_id: UUID
    last_updated: datetime


# ── Blood Request schemas ─────────────────────────────────────
class BloodRequestBase(BaseSchema):
    blood_group: str
    units_needed: int
    district_id: Optional[int]
    hospital_id: Optional[UUID]
    hospital_name: Optional[str] = None
    hospital_cabin: Optional[str] = None
    urgency_level: UrgencyLevel
    status: RequestStatus
    nid_number: Optional[str] = None
    nid_name: Optional[str] = None
    nid_dob: Optional[str] = None
    nid_image_url: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING_VERIFICATION
    admin_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    patient_name: Optional[str]
    patient_condition: Optional[str]
    required_by: Optional[date]
    contact_phone: Optional[str]


class BloodRequestCreate(BaseModel):
    blood_group: str = Field(..., pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    units_needed: int = Field(..., ge=1, le=10)
    district_id: Optional[int] = None
    district: Optional[str] = None
    division: Optional[str] = None
    hospital_id: Optional[UUID] = None
    hospital_name: Optional[str] = None
    hospital_cabin: Optional[str] = None
    nid_number: Optional[str] = None
    nid_name: Optional[str] = None
    nid_dob: Optional[str] = None
    nid_image_url: Optional[str] = None
    urgency_level: UrgencyLevel = UrgencyLevel.NORMAL
    patient_name: Optional[str] = Field(None, max_length=150)
    patient_condition: Optional[str] = None
    required_by: Optional[date] = None
    contact_phone: Optional[str] = Field(None, max_length=20)


class BloodRequestUpdate(BaseModel):
    units_needed: Optional[int] = Field(None, ge=1, le=10)
    district_id: Optional[int] = None
    hospital_id: Optional[UUID] = None
    hospital_name: Optional[str] = None
    hospital_cabin: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    status: Optional[RequestStatus] = None
    verification_status: Optional[VerificationStatus] = None
    admin_notes: Optional[str] = None
    patient_name: Optional[str] = Field(None, max_length=150)
    patient_condition: Optional[str] = None
    required_by: Optional[date] = None
    contact_phone: Optional[str] = Field(None, max_length=20)


class AdminVerifyRequest(BaseModel):
    action: str = Field(..., pattern=r"^(APPROVE|REJECT|FLAG_FRAUD)$")
    admin_notes: Optional[str] = None


class BloodRequestResponse(BloodRequestBase):
    request_id: UUID
    seeker_id: UUID
    created_at: datetime
    updated_at: datetime


class BloodRequestWithSeeker(BloodRequestResponse):
    seeker: Optional[UserResponse] = None


class PublicBloodRequestResponse(BaseModel):
    request_id: UUID
    blood_group: str
    units_needed: int
    urgency_level: UrgencyLevel
    required_by: Optional[date] = None
    district: Optional[str] = None
    division: Optional[str] = None
    created_at: datetime


# ── Request Match schemas ─────────────────────────────────────
class RequestMatchBase(BaseSchema):
    status: MatchStatus
    notes: Optional[str]


class RequestMatchCreate(BaseModel):
    request_id: UUID
    donor_id: UUID
    notes: Optional[str] = None


class RequestMatchUpdate(BaseModel):
    status: Optional[MatchStatus] = None
    notes: Optional[str] = None


class RequestMatchResponse(RequestMatchBase):
    match_id: UUID
    request_id: UUID
    donor_id: UUID
    matched_at: datetime
    responded_at: Optional[datetime]


class RequestMatchWithDetails(RequestMatchResponse):
    request: Optional[BloodRequestResponse] = None
    donor: Optional[DonorResponse] = None


# ── Donation schemas ──────────────────────────────────────────
class DonationBase(BaseSchema):
    blood_group: str
    units_donated: int
    donation_date: date
    notes: Optional[str]


class DonationCreate(BaseModel):
    match_id: Optional[UUID] = None
    donor_id: Optional[UUID] = None
    request_id: Optional[UUID] = None
    hospital_id: Optional[UUID] = None
    blood_group: str = Field(..., pattern=r"^(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)$")
    units_donated: int = Field(..., ge=1, le=10)
    donation_date: date = Field(default_factory=date.today)
    verified_by: Optional[UUID] = None
    notes: Optional[str] = None


class DonationResponse(DonationBase):
    donation_id: UUID
    match_id: Optional[UUID]
    donor_id: UUID
    request_id: Optional[UUID]
    hospital_id: Optional[UUID]
    created_at: datetime


# ── Notification schemas ──────────────────────────────────────
class NotificationBase(BaseSchema):
    title: str
    message: str
    type: NotificationType
    is_read: bool


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str = Field(..., max_length=200)
    message: str
    type: NotificationType = NotificationType.SYSTEM
    related_request_id: Optional[UUID] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    notif_id: UUID
    user_id: UUID
    related_request_id: Optional[UUID]
    created_at: datetime


# ── Audit Log schemas ─────────────────────────────────────────
class AuditLogBase(BaseSchema):
    action: str
    target_table: Optional[str]
    target_id: Optional[UUID]
    details: Optional[dict]
    ip_address: Optional[str]


class AuditLogCreate(BaseModel):
    actor_id: Optional[UUID] = None
    action: str = Field(..., max_length=100)
    target_table: Optional[str] = None
    target_id: Optional[UUID] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    log_id: UUID
    actor_id: Optional[UUID]
    created_at: datetime




# ── Analytics schemas ─────────────────────────────────────────
class DashboardStats(BaseSchema):
    total_donors: int
    available_donors: int
    total_seekers: int
    total_hospitals: int
    total_requests: int
    districts_covered: int
    fulfillment_rate: float
    pending_requests: int
    critical_requests: int
    fulfilled_today: int
    low_stock_alerts: int


class DivisionStats(BaseSchema):
    division: str
    donors: int
    seekers: int
    hospitals: int
    coverage: str


class BloodGroupStats(BaseSchema):
    blood_group: str
    available_donors: int
    pending_requests: int
    hospital_stock: int


# Forward references
UserProfileResponse.model_rebuild()
DonorResponse.model_rebuild()
HospitalResponse.model_rebuild()
BloodRequestWithSeeker.model_rebuild()
RequestMatchWithDetails.model_rebuild()