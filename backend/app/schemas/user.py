import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.utils.enums import Role


class UserOut(BaseModel):
    user_id: uuid.UUID
    name: str
    email: EmailStr
    role: Role
    district_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str | None = None
    district_id: int | None = None
