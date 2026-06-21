import uuid
from datetime import datetime

from pydantic import BaseModel


class HospitalInventoryOut(BaseModel):
    inv_id: uuid.UUID
    hospital_id: uuid.UUID
    blood_group: str
    units_available: int
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryUnitsUpdate(BaseModel):
    units_available: int
