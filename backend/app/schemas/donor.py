import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DonorOut(BaseModel):
    donor_id: uuid.UUID
    user_id: uuid.UUID
    blood_group: str
    is_available: bool
    last_donated: date | None
    total_donations: int
    created_at: datetime

    class Config:
        from_attributes = True


class DonorAvailabilityUpdate(BaseModel):
    is_available: bool
