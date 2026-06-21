import uuid
from datetime import datetime

from pydantic import BaseModel


class DonationOut(BaseModel):
    donation_id: uuid.UUID
    match_id: uuid.UUID
    donor_id: uuid.UUID
    request_id: uuid.UUID
    donated_at: datetime

    class Config:
        from_attributes = True
