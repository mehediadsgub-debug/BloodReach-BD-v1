import uuid
from datetime import datetime

from pydantic import BaseModel


class HospitalOut(BaseModel):
    hospital_id: uuid.UUID
    name: str
    district_id: int
    admin_user_id: uuid.UUID
    contact_info: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class HospitalUpdate(BaseModel):
    name: str | None = None
    contact_info: str | None = None
