"""
BloodReach BD — Authentication Service
Handles password hashing, JWT token generation/validation, and refresh token rotation.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.models import User, UserRole
from app.schemas import TokenResponse


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, role: UserRole, email: str) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "role": role.value,
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_tokens(user: User) -> TokenResponse:
    """Create both access and refresh tokens for a user"""
    access_token = create_access_token(user.user_id, user.role, user.email)
    refresh_token = create_refresh_token(user.user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name
    )


def get_user_from_token(token: str) -> Optional[dict]:
    """Extract user info from token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return {
            "user_id": UUID(payload["sub"]),
            "role": UserRole(payload["role"]),
            "email": payload["email"]
        }
    return None


def refresh_access_token(refresh_token: str) -> Optional[TokenResponse]:
    """Refresh access token using refresh token"""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None

    user_id = UUID(payload["sub"])
    # In a real app, you'd fetch the user from DB to get current role/email
    # For now, we'll just create a new access token
    # This should be enhanced to fetch actual user data
    return None  # Will be implemented with DB lookup