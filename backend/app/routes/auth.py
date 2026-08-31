"""
BloodReach BD — Authentication Routes
Login, register, token refresh, logout.
"""

import re
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
    # Resolve email and phone (at least one must be provided)
    raw_email = request.email
    raw_phone = request.phone

    if not raw_email and not raw_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number or Email is required"
        )

    # If email is not provided, create a standard phone-based system email
    if not raw_email:
        clean_digits = re.sub(r"[^\d]", "", raw_phone)
        raw_email = f"{clean_digits}@bloodreach.local"

    # Check if email exists
    if db.query(User).filter(User.email == raw_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Account already registered"
        )

    # Check phone if provided
    if raw_phone and db.query(User).filter(User.phone == raw_phone).first():
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

    # Canonical spelling mappings for Bangladesh divisions & districts
    DIVISION_ALIASES = {
        "dhaka": "Dhaka",
        "chattogram": "Chattogram",
        "chittagong": "Chattogram",
        "rajshahi": "Rajshahi",
        "khulna": "Khulna",
        "barishal": "Barishal",
        "barisal": "Barishal",
        "sylhet": "Sylhet",
        "rangpur": "Rangpur",
        "mymensingh": "Mymensingh",
    }

    DISTRICT_ALIASES = {
        "bogra": "Bogura",
        "bogura": "Bogura",
        "jessore": "Jashore",
        "jashore": "Jashore",
        "comilla": "Comilla",
        "cumilla": "Comilla",
        "chattogram": "Chattogram",
        "chittagong": "Chattogram",
        "barisal": "Barishal",
        "barishal": "Barishal",
        "coxs bazar": "Cox's Bazar",
        "cox's bazar": "Cox's Bazar",
        "coxsbazar": "Cox's Bazar",
        "netrakona": "Netrokona",
        "netrokona": "Netrokona",
        "chapainawabganj": "Chapainawabganj",
        "chapai nawabganj": "Chapainawabganj",
        "moulvibazar": "Moulvibazar",
        "moulvi bazar": "Moulvibazar",
        "brahmanbaria": "Brahmanbaria",
    }

    if district_id is None and request.district:
        raw_dist = request.district.strip()
        clean_dist = DISTRICT_ALIASES.get(raw_dist.lower(), raw_dist)

        # Look up division by name, then district by (name, division)
        if division_id is None and request.division:
            raw_div = request.division.strip()
            clean_div = DIVISION_ALIASES.get(raw_div.lower(), raw_div)
            division = db.query(Division).filter(
                (Division.name.ilike(clean_div)) | (Division.name.ilike(raw_div))
            ).first()
            if division:
                division_id = division.division_id

        # 1. Try matching clean_dist with division_id filter if present
        query = db.query(District).filter(
            (District.name.ilike(clean_dist)) | (District.name.ilike(raw_dist))
        )
        if division_id is not None:
            district = query.filter(District.division_id == division_id).first()
        else:
            district = query.first()

        # 2. Fallback: match without division_id filter
        if not district:
            district = db.query(District).filter(
                (District.name.ilike(clean_dist)) | (District.name.ilike(raw_dist))
            ).first()

        # 3. Fallback: partial match
        if not district:
            district = db.query(District).filter(District.name.ilike(f"%{clean_dist}%")).first()

        if district:
            district_id = district.district_id
        elif request.role == UserRole.DONOR:
            # If district database table is completely unseeded, fallback to first available or error
            fallback_dist = db.query(District).first()
            if fallback_dist:
                district_id = fallback_dist.district_id
            else:
                district_id = None

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
        email=raw_email,
        phone=raw_phone,
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
            contact_email=raw_email,
            contact_phone=raw_phone
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