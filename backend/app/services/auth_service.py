"""Business logic for registration, login, and JWT token issuance."""

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceError
from app.core.security import hash_password, verify_password, create_access_token


def register_user(payload, db: Session):
    # TODO:
    # 1. check if payload.email already exists -> raise DuplicateResourceError
    # 2. hash payload.password with hash_password()
    # 3. persist new User row
    # 4. return the created user
    raise NotImplementedError


def authenticate_user(payload, db: Session):
    # TODO:
    # 1. fetch user by email
    # 2. verify_password(payload.password, user.password_hash)
    # 3. create_access_token({"sub": str(user.user_id), "role": user.role})
    # 4. return TokenResponse
    raise NotImplementedError
