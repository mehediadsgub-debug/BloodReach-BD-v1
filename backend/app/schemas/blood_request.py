import uuid
from datetime import datetime

from pydantic import BaseModel

from app.utils.enums import UrgencyLevel, RequestStatus


class BloodRequestCreate(BaseModel):
    district_id: int
    blood_group: str
    quantity_units: int
    urgency_level: UrgencyLevel


class BloodRequestOut(BaseModel):
    request_id: uuid.UUID
    seeker_id: uuid.UUID
    district_id: int
    blood_group: str
    quantity_units: int
    urgency_level: UrgencyLevel
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
