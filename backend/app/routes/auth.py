"""
BloodReach BD — Authentication Routes
Login, register, token refresh, logout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User, UserRole, Donor, Hospital, Division, District
from app.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest,
    UserCreate, UserResponse, DonorCreate, DonorResponse
)
from app.services import (
    hash_password, verify_password, create_tokens, decode_token
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login with email or phone number, password, and role"""
    identifier = request.email.strip()
    user = db.query(User).filter(or_(User.email == identifier, User.phone == identifier)).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Verify role matches
    if user.role != request.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid role. You are registered as {user.role.value}"
        )

    # Create tokens
    tokens = create_tokens(user)

    # Create donor profile if needed and doesn't exist
    if user.role == UserRole.DONOR and not user.donor_profile:
        # Will be created via separate profile completion endpoint
        pass

    return tokens


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check phone if provided
    if request.phone and db.query(User).filter(User.phone == request.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Resolve full name (frontend may send `name` instead of `full_name`)
    full_name = (request.full_name or request.name or "").strip()
    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name is required"
        )

    # Resolve district_id from either an id or a district+division name
    district_id = request.district_id
    division_id = request.division_id

    if district_id is None and request.district:
        clean_dist = request.district.strip()
        # Look up division by name, then district by (name, division)
        if division_id is None and request.division:
            clean_div = request.division.strip()
            division = db.query(Division).filter(Division.name.ilike(clean_div)).first()
            if not division:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown division: {request.division}"
                )
            division_id = division.division_id

        district = db.query(District).filter(District.name.ilike(clean_dist))
        if division_id is not None:
            district = district.filter(District.division_id == division_id)
        district = district.first()

        if not district:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown district: {request.district}"
            )
        district_id = district.district_id

    # Validate donor-specific fields
    if request.role == UserRole.DONOR:
        if not request.blood_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Blood group is required for donors"
            )
        clean_bg = request.blood_group.replace(" ", "+").strip().upper()
        if not district_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="District is required for donors"
            )

    # Create user
    user = User(
        full_name=full_name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        role=request.role,
        district_id=district_id,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.flush()

    # Create role-specific profile
    if request.role == UserRole.DONOR:
        clean_bg = request.blood_group.replace(" ", "+").strip().upper()
        donor = Donor(
            user_id=user.user_id,
            blood_group=clean_bg,
            is_available=True
        )
        db.add(donor)

    elif request.role == UserRole.HOSPITAL_ADMIN:
        hospital = Hospital(
            name=full_name,  # Use name as hospital name initially
            admin_user_id=user.user_id,
            district_id=district_id,
            contact_email=request.email,
            contact_phone=request.phone
        )
        db.add(hospital)

    db.commit()
    db.refresh(user)

    # Create tokens
    tokens = create_tokens(user)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = UUID(payload["sub"])
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    tokens = create_tokens(user)
    return tokens


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile information"""
    return current_user


@router.post("/logout")
def logout():
    """Logout endpoint (client-side token removal)"""
    # In a stateless JWT system, logout is handled client-side
    # For server-side logout, you'd need a token blacklist (Redis)
    return {"message": "Successfully logged out"}