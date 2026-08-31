"""
BloodReach BD — Authentication Dependencies
FastAPI dependencies for getting current user, role-based access control.
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import get_user_from_token
from app.models import User, UserRole
from app.schemas import TokenResponse


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    user_data = get_user_from_token(credentials.credentials)
    if not user_data:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == user_data["user_id"]).first()
    if not user or not user.is_active:
        raise credentials_exception

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Safely get current authenticated user if token is provided, else return None"""
    if not credentials or not credentials.credentials:
        return None

    user_data = get_user_from_token(credentials.credentials)
    if not user_data:
        return None

    user = db.query(User).filter(User.user_id == user_data["user_id"]).first()
    if not user or not user.is_active:
        return None

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


# Pre-defined role dependencies
require_donor = require_role(UserRole.DONOR)
require_seeker = require_role(UserRole.SEEKER)
require_hospital_admin = require_role(UserRole.HOSPITAL_ADMIN)
require_superadmin = require_role(UserRole.SUPERADMIN)
require_any_admin = require_role(UserRole.HOSPITAL_ADMIN, UserRole.SUPERADMIN)
require_donor_or_seeker = require_role(UserRole.DONOR, UserRole.SEEKER)