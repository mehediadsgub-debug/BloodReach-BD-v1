"""
BloodReach BD — User Routes
Profile management, donor profile, hospital profile.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    require_donor,
    require_hospital_admin,
    require_superadmin
)
from app.models import User, UserRole, Donor, Hospital, Division, District, HospitalInventory, AuditLog
from app.schemas import (
    UserUpdate, UserResponse, UserProfileResponse, UserStatusUpdate,
    DonorCreate, DonorUpdate, DonorResponse,
    HospitalUpdate, HospitalResponse, ProfileUpdateRequest,
    InventoryResponse
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's full profile including role-specific data"""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Check email uniqueness if changed
    if update_data.email and update_data.email != current_user.email:
        if db.query(User).filter(User.email == update_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    # Check phone uniqueness if changed
    if update_data.phone and update_data.phone != current_user.phone:
        if db.query(User).filter(User.phone == update_data.phone).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )

    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get another user's profile (for matching, etc.)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# ── Donor Profile Routes ──────────────────────────────────────

@router.post("/me/donor-profile", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor_profile(
    profile_data: DonorCreate,
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Create donor profile for current user"""
    if current_user.donor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donor profile already exists"
        )

    donor = Donor(
        user_id=current_user.user_id,
        **profile_data.model_dump()
    )
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.get("/me/donor-profile", response_model=DonorResponse)
def get_my_donor_profile(current_user: User = Depends(require_donor)):
    """Get current user's donor profile"""
    if not current_user.donor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )
    return current_user.donor_profile


@router.patch("/me/donor-profile", response_model=DonorResponse)
def update_my_donor_profile(
    update_data: DonorUpdate,
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Update current user's donor profile"""
    if not current_user.donor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user.donor_profile, field, value)

    db.commit()
    db.refresh(current_user.donor_profile)
    return current_user.donor_profile


@router.patch("/me/availability", response_model=DonorResponse)
def update_availability(
    is_available: bool,
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Update donor availability status"""
    if not current_user.donor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    current_user.donor_profile.is_available = is_available
    db.commit()
    db.refresh(current_user.donor_profile)
    return current_user.donor_profile


# ── Hospital Profile Routes ───────────────────────────────────

@router.get("/me/hospital-profile", response_model=HospitalResponse)
def get_my_hospital_profile(current_user: User = Depends(require_hospital_admin)):
    """Get current user's hospital profile"""
    if not current_user.hospital_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )
    return current_user.hospital_admin


@router.patch("/me/hospital-profile", response_model=HospitalResponse)
def update_my_hospital_profile(
    update_data: HospitalUpdate,
    current_user: User = Depends(require_hospital_admin),
    db: Session = Depends(get_db)
):
    """Update current user's hospital profile"""
    if not current_user.hospital_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user.hospital_admin, field, value)

    db.commit()
    db.refresh(current_user.hospital_admin)
    return current_user.hospital_admin


@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile_and_donor_info(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile settings (name, email, phone, division, district, blood_group, is_available)"""
    # 1. Update User basic info
    new_name = (request.full_name or request.name)
    if new_name is not None and new_name.strip():
        current_user.full_name = new_name.strip()

    if request.email is not None:
        email = request.email.strip().lower()
        if email != current_user.email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = email

    if request.phone is not None and request.phone.strip():
        phone = request.phone.strip()
        if phone != current_user.phone:
            existing_phone = db.query(User).filter(User.phone == phone).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already in use"
                )
            current_user.phone = phone

    # 2. Update location (division + district)
    if request.division and request.district:
        clean_div = request.division.strip()
        clean_dist = request.district.strip()
        division = db.query(Division).filter(Division.name.ilike(clean_div)).first()
        if division:
            district = db.query(District).filter(
                and_(District.name.ilike(clean_dist), District.division_id == division.division_id)
            ).first()
            if district:
                current_user.district_id = district.district_id
    elif request.district:
        clean_dist = request.district.strip()
        district = db.query(District).filter(District.name.ilike(clean_dist)).first()
        if district:
            current_user.district_id = district.district_id

    # 3. Update Donor profile if the user's role is DONOR
    if current_user.role == UserRole.DONOR:
        donor = current_user.donor_profile
        if not donor:
            donor = Donor(
                user_id=current_user.user_id,
                blood_group=(request.blood_group or "O+").replace(" ", "+").strip().upper(),
                is_available=True if request.is_available is None else request.is_available
            )
            db.add(donor)
            db.flush()
        else:
            if request.blood_group is not None and request.blood_group.strip():
                donor.blood_group = request.blood_group.replace(" ", "+").strip().upper()
            if request.is_available is not None:
                donor.is_available = request.is_available

    db.commit()
    db.refresh(current_user)
    return current_user


# ── Hospital Inventory Management Endpoints ─────────────────────────────────

@router.get("/me/hospital-inventory", response_model=List[InventoryResponse])
def get_my_hospital_inventory(
    current_user: User = Depends(require_hospital_admin),
    db: Session = Depends(get_db)
):
    """Get the blood inventory for the logged-in hospital administrator's hospital"""
    hospital = current_user.hospital_admin
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this administrator."
        )
    
    # Check if inventory is seeded. If not, seed default 0 values for all 8 blood groups
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    existing_inventory = {inv.blood_group: inv for inv in hospital.inventory}
    
    seeded_any = False
    for bg in blood_groups:
        if bg not in existing_inventory:
            new_inv = HospitalInventory(
                hospital_id=hospital.hospital_id,
                blood_group=bg,
                units_available=0,
                low_stock_alert=5
            )
            db.add(new_inv)
            seeded_any = True
            
    if seeded_any:
        db.commit()
        db.refresh(hospital)
        
    return hospital.inventory


class InventoryUpdatePayload(BaseModel):
    blood_group: str
    units_available: int


@router.put("/me/hospital-inventory", response_model=InventoryResponse)
def update_my_hospital_inventory(
    payload: InventoryUpdatePayload,
    current_user: User = Depends(require_hospital_admin),
    db: Session = Depends(get_db)
):
    """Update stock level for a specific blood group in the hospital's inventory"""
    hospital = current_user.hospital_admin
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this administrator."
        )
        
    # Validation
    bg = payload.blood_group.strip().upper()
    if bg not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid blood group: {payload.blood_group}"
        )
        
    if payload.units_available < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock units cannot be negative."
        )
        
    # Find existing or create
    inv_item = db.query(HospitalInventory).filter(
        and_(
            HospitalInventory.hospital_id == hospital.hospital_id,
            HospitalInventory.blood_group == bg
        )
    ).first()
    
    if not inv_item:
        inv_item = HospitalInventory(
            hospital_id=hospital.hospital_id,
            blood_group=bg,
            units_available=payload.units_available,
            low_stock_alert=5
        )
        db.add(inv_item)
    else:
        inv_item.units_available = payload.units_available
        inv_item.last_updated = datetime.now()
        
    db.commit()
    db.refresh(inv_item)
    return inv_item


class InventoryAdjustPayload(BaseModel):
    blood_group: str
    delta_units: int  # e.g., -1 for dispatch, +2 for received


@router.post("/me/hospital-inventory/adjust", response_model=InventoryResponse)
def adjust_my_hospital_inventory(
    payload: InventoryAdjustPayload,
    current_user: User = Depends(require_hospital_admin),
    db: Session = Depends(get_db)
):
    """Atomically increment or decrement blood stock units to avoid race conditions"""
    hospital = current_user.hospital_admin
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this administrator."
        )

    bg = payload.blood_group.strip().upper()
    if bg not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid blood group: {payload.blood_group}"
        )

    inv_item = db.query(HospitalInventory).filter(
        and_(
            HospitalInventory.hospital_id == hospital.hospital_id,
            HospitalInventory.blood_group == bg
        )
    ).first()

    if not inv_item:
        if payload.delta_units < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deduct stock. No inventory record exists for {bg}."
            )
        inv_item = HospitalInventory(
            hospital_id=hospital.hospital_id,
            blood_group=bg,
            units_available=payload.delta_units,
            low_stock_alert=5
        )
        db.add(inv_item)
    else:
        new_total = inv_item.units_available + payload.delta_units
        if new_total < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient blood units. Available: {inv_item.units_available}, Requested deduction: {abs(payload.delta_units)}."
            )
        inv_item.units_available = new_total
        inv_item.last_updated = datetime.now()

    db.commit()
    db.refresh(inv_item)
    return inv_item


# ── Superadmin User Management Endpoints ────────────────────────────────────

@router.get("/", response_model=List[UserResponse])
def list_all_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    query: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter active/inactive"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """List all registered platform users with search and filters (Superadmin only)"""
    stmt = db.query(User)

    if role:
        stmt = stmt.filter(User.role == role)
    if is_active is not None:
        stmt = stmt.filter(User.is_active == is_active)
    if query:
        search_pattern = f"%{query.strip()}%"
        stmt = stmt.filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.phone.ilike(search_pattern)
            )
        )

    return stmt.order_by(User.created_at.desc()).limit(limit).all()


@router.patch("/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    user_id: UUID,
    status_data: UserStatusUpdate,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a user account (Superadmin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = status_data.is_active

    # Log audit event
    action = "USER_ACTIVATED" if status_data.is_active else "USER_DEACTIVATED"
    audit = AuditLog(
        actor_id=current_user.user_id,
        action=action,
        target_table="users",
        target_id=user.user_id,
        details={"user_email": user.email, "role": user.role.value, "is_active": user.is_active}
    )
    db.add(audit)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Delete a user account and associated profile (Superadmin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Log audit event before deletion
    audit = AuditLog(
        actor_id=current_user.user_id,
        action="USER_DELETED",
        target_table="users",
        target_id=user.user_id,
        details={"user_email": user.email, "role": user.role.value, "user_name": user.full_name}
    )
    db.add(audit)

    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} successfully deleted"}