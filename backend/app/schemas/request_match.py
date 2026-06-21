import uuid
from datetime import datetime

from pydantic import BaseModel

from app.utils.enums import MatchStatus


class RequestMatchOut(BaseModel):
    match_id: uuid.UUID
    request_id: uuid.UUID
    donor_id: uuid.UUID
    status: MatchStatus
    responded_at: datetime | None
    fulfilled_at: datetime | None

    class Config:
        from_attributes = True
