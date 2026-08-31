"""
BloodReach BD — Donor Routes
Donor search, profile details, and donation history.
"""

from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_donor, get_optional_current_user
from app.models import User, UserRole, Donor, Donation, District, Division, RequestMatch, BloodRequest, VerificationStatus
from app.schemas import (
    DonorResponse,
    DonorSearchResult,
    DonationResponse,
    DonationCreate
)

router = APIRouter(prefix="/api/v1/donors", tags=["Donors"])


@router.get("/search", response_model=List[DonorSearchResult])
def search_donors(
    blood_group: Optional[str] = Query(None, description="Filter by blood group e.g. A+, O-"),
    division: Optional[str] = Query(None, description="Division name"),
    district: Optional[str] = Query(None, description="District name"),
    district_id: Optional[int] = Query(None, description="District ID"),
    is_available_only: bool = Query(True, description="Only available donors"),
    limit: int = Query(50, ge=1, le=200),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Search donors across Bangladesh with optional filters for blood group, division, and district.
    Phone numbers are unlocked only when Admin has approved the seeker's blood request.
    """
    query = (
        db.query(Donor)
        .join(User, Donor.user_id == User.user_id)
        .outerjoin(District, User.district_id == District.district_id)
        .outerjoin(Division, District.division_id == Division.division_id)
        .filter(User.is_active == True)
    )

    if is_available_only:
        query = query.filter(Donor.is_available == True)

    if blood_group and blood_group.strip() and "ALL" not in blood_group.strip().upper():
        clean_bg = blood_group.replace(" ", "+").strip().upper()
        query = query.filter(Donor.blood_group == clean_bg)

    if district_id:
        query = query.filter(User.district_id == district_id)
    elif district and district.strip() and "ALL" not in district.strip().upper():
        query = query.filter(District.name.ilike(f"%{district.strip()}%"))

    if division and division.strip() and "ALL" not in division.strip().upper():
        query = query.filter(Division.name.ilike(f"%{division.strip()}%"))

    donors = query.order_by(Donor.last_donation_date.asc().nullsfirst(), Donor.total_donations.desc()).limit(limit).all()

    # Determine if phone number should be revealed
    can_view_phones = False
    if current_user:
        if current_user.role in [UserRole.SUPERADMIN, UserRole.HOSPITAL_ADMIN, UserRole.DONOR]:
            can_view_phones = True
        elif current_user.role == UserRole.SEEKER:
            # Check if this seeker has at least one request approved by admin
            has_approved_request = db.query(BloodRequest).filter(
                and_(
                    BloodRequest.seeker_id == current_user.user_id,
                    BloodRequest.verification_status == VerificationStatus.APPROVED
                )
            ).first() is not None
            if has_approved_request:
                can_view_phones = True

    results = []
    for d in donors:
        user = d.user
        donor_phone = user.phone if (user and can_view_phones) else None
        results.append(
            DonorSearchResult(
                donor_id=d.donor_id,
                full_name=user.full_name if user else "Anonymous Donor",
                blood_group=d.blood_group,
                is_available=d.is_available,
                division=d.division,
                district=d.district,
                last_donation_date=d.last_donation_date,
                total_donations=d.total_donations,
                phone=donor_phone,
                is_phone_unlocked=can_view_phones
            )
        )
    return results


@router.get("/me/history", response_model=List[DonationResponse])
def get_my_donation_history(
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Get complete donation history for the currently logged-in donor"""
    donor = current_user.donor_profile
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    donations = db.query(Donation).filter(Donation.donor_id == donor.donor_id).order_by(Donation.donation_date.desc()).all()
    return donations


@router.post("/me/donations", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def record_donation(
    payload: DonationCreate,
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Record a completed donation for the donor and update total donations count"""
    donor = current_user.donor_profile
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    donation = Donation(
        donor_id=donor.donor_id,
        match_id=payload.match_id,
        request_id=payload.request_id,
        hospital_id=payload.hospital_id,
        blood_group=payload.blood_group or donor.blood_group,
        units_donated=payload.units_donated,
        donation_date=payload.donation_date or date.today(),
        notes=payload.notes
    )
    db.add(donation)

    # Update donor stats
    donor.total_donations += payload.units_donated
    donor.last_donation_date = donation.donation_date

    db.commit()
    db.refresh(donation)
    return donation


@router.get("/{donor_id}", response_model=DonorResponse)
def get_donor_details(
    donor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get public donor information by donor ID"""
    donor = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    return donor
