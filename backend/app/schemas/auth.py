from pydantic import BaseModel, EmailStr

from app.utils.enums import Role


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role
    district_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
