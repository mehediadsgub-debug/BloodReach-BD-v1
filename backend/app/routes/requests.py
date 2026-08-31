"""
BloodReach BD — Blood Request and Matching Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    require_donor,
    require_seeker,
    require_any_admin
)
from app.models import (
    User,
    UserRole,
    Donor,
    BloodRequest,
    RequestMatch,
    MatchStatus,
    UrgencyLevel,
    RequestStatus,
    VerificationStatus,
    District
)
from app.schemas import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestWithSeeker,
    BloodRequestUpdate,
    RequestMatchResponse,
    RequestMatchWithDetails,
    PublicBloodRequestResponse
)
from app.services.matching_service import MatchingEngine
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/requests", tags=["Blood Requests"])


@router.post("/", response_model=BloodRequestResponse, status_code=status.HTTP_201_CREATED)
def create_blood_request(
    request_data: BloodRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new blood request with NID anti-fraud info (queued for admin approval)"""
    if current_user.role == UserRole.DONOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Donors cannot post blood requests. Please register/login as a Seeker."
        )

    # Determine seeker_id and district_id
    seeker_id = current_user.user_id
    district_id = request_data.district_id

    if district_id is None and request_data.district:
        district = db.query(District).filter(District.name.ilike(request_data.district.strip())).first()
        if district:
            district_id = district.district_id

    if district_id is None:
        district_id = current_user.district_id

    if not district_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify a district for the blood request."
        )

    # Create Blood Request with NID anti-fraud verification fields
    db_request = BloodRequest(
        seeker_id=seeker_id,
        blood_group=request_data.blood_group,
        units_needed=request_data.units_needed,
        district_id=district_id,
        hospital_id=request_data.hospital_id,
        hospital_name=request_data.hospital_name,
        hospital_cabin=request_data.hospital_cabin,
        nid_number=request_data.nid_number,
        nid_name=request_data.nid_name,
        nid_dob=request_data.nid_dob,
        nid_image_url=request_data.nid_image_url,
        verification_status=VerificationStatus.PENDING_VERIFICATION,
        urgency_level=request_data.urgency_level,
        status=RequestStatus.OPEN,
        patient_name=request_data.patient_name,
        patient_condition=request_data.patient_condition,
        required_by=request_data.required_by,
        contact_phone=request_data.contact_phone
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Pre-generate match candidates
    try:
        from app.services.matching_service import MatchingEngine
        matcher = MatchingEngine(db)
        matcher.auto_match_request(db_request)
    except Exception as e:
        print(f"[WARN] Automatic donor matching failed: {e}")

    return db_request


@router.get("/", response_model=List[BloodRequestWithSeeker])
def list_blood_requests(
    status_filter: Optional[RequestStatus] = None,
    blood_group: Optional[str] = None,
    district_id: Optional[int] = None,
    urgency_level: Optional[UrgencyLevel] = None,
    my_requests_only: bool = False,
    matched_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List blood requests with filters. Seekers view their own by default if my_requests_only is set."""
    query = db.query(BloodRequest)

    # 1. Apply user role defaults / specific constraints
    if my_requests_only or current_user.role == UserRole.SEEKER:
        # Seekers default to seeing their own requests
        if current_user.role == UserRole.SEEKER or my_requests_only:
            query = query.filter(BloodRequest.seeker_id == current_user.user_id)

    if matched_only and current_user.role == UserRole.DONOR:
        donor = current_user.donor_profile
        if not donor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Donor profile not found."
            )
        # Filter requests where a match exists for this donor
        query = query.join(RequestMatch).filter(RequestMatch.donor_id == donor.donor_id)
    elif current_user.role == UserRole.DONOR:
        # Donors browsing all requests only see admin-verified approved requests
        query = query.filter(BloodRequest.verification_status == VerificationStatus.APPROVED)

    # 2. Apply query filters
    if status_filter:
        query = query.filter(BloodRequest.status == status_filter)
    if blood_group:
        clean_bg = blood_group.replace(" ", "+").strip().upper()
        query = query.filter(BloodRequest.blood_group == clean_bg)
    if district_id:
        query = query.filter(BloodRequest.district_id == district_id)
    if urgency_level:
        query = query.filter(BloodRequest.urgency_level == urgency_level)

    return query.order_by(BloodRequest.created_at.desc()).all()


@router.get("/public", response_model=List[PublicBloodRequestResponse])
def list_public_blood_requests(
    blood_group: Optional[str] = None,
    district_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List anonymized active seeker requests for the public matching page."""
    limit = min(max(limit, 1), 50)
    query = (
        db.query(BloodRequest)
        .join(District, BloodRequest.district_id == District.district_id, isouter=True)
        .filter(BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.IN_PROGRESS]))
    )

    if blood_group:
        query = query.filter(BloodRequest.blood_group == blood_group.replace(" ", "+").strip().upper())
    if district_id:
        query = query.filter(BloodRequest.district_id == district_id)

    requests = query.order_by(BloodRequest.created_at.desc()).limit(limit).all()
    return [
        {
            "request_id": request.request_id,
            "blood_group": request.blood_group,
            "units_needed": request.units_needed,
            "urgency_level": request.urgency_level,
            "required_by": request.required_by,
            "district": request.district.name if request.district else None,
            "division": request.district.division.name if request.district and request.district.division else None,
            "created_at": request.created_at,
        }
        for request in requests
    ]


@router.get("/matches/pending", response_model=List[RequestMatchWithDetails])
def get_my_pending_matches(
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Get all pending matches for the logged-in donor"""
    donor = current_user.donor_profile
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found."
        )

    engine = MatchingEngine(db)
    return engine.get_pending_matches_for_donor(donor.donor_id)


@router.post("/matches/{match_id}/respond", response_model=RequestMatchResponse)
def respond_to_match_request(
    match_id: UUID,
    accept: bool,
    notes: Optional[str] = None,
    current_user: User = Depends(require_donor),
    db: Session = Depends(get_db)
):
    """Respond (accept/reject) to a pending match request"""
    donor = current_user.donor_profile
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found."
        )

    engine = MatchingEngine(db)
    try:
        match = engine.respond_to_match(
            match_id=match_id,
            donor_id=donor.donor_id,
            accept=accept,
            notes=notes
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending match request not found, or it has already been responded to."
        )

    # Notify seeker if match accepted
    if accept:
        notif_service = NotificationService(db)
        notif_service.notify_request_fulfilled(
            seeker_user_id=match.request.seeker_id,
            request=match.request,
            donor_name=current_user.full_name
        )

    return match


@router.get("/{request_id}", response_model=BloodRequestWithSeeker)
def get_blood_request(
    request_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information of a blood request"""
    request = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )
    return request


@router.get("/{request_id}/matches", response_model=List[RequestMatchWithDetails])
def get_request_matches(
    request_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all matching donor records for a specific blood request"""
    request = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )

    # Check permission (only seeker who created it or admins can view matches)
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.HOSPITAL_ADMIN] and request.seeker_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view matches for this request."
        )

    return db.query(RequestMatch).filter(RequestMatch.request_id == request_id).all()


@router.post("/{request_id}/match-manually", response_model=List[RequestMatchResponse])
def match_request_manually(
    request_id: UUID,
    donor_ids: List[UUID],
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually match specific donors to a request"""
    request = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )

    # Check permission
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.HOSPITAL_ADMIN] and request.seeker_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to match donors for this request."
        )

    engine = MatchingEngine(db)
    matches = engine.create_matches(request, donor_ids, notes)

    # Notify donors
    notif_service = NotificationService(db)
    for match in matches:
        donor = db.query(Donor).filter(Donor.donor_id == match.donor_id).first()
        if donor and donor.user_id:
            notif_service.notify_donor_match(donor.user_id, request, match.match_id)

    return matches


@router.patch("/{request_id}", response_model=BloodRequestResponse)
def update_blood_request(
    request_id: UUID,
    update_data: BloodRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update properties of a blood request"""
    request = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )

    # Check permission
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.HOSPITAL_ADMIN] and request.seeker_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this request."
        )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}", response_model=BloodRequestResponse)
def cancel_blood_request(
    request_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a blood request and cancel any associated pending match requests"""
    request = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )

    # Check permission
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.HOSPITAL_ADMIN] and request.seeker_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this request."
        )

    # Set request status to CANCELLED
    request.status = RequestStatus.CANCELLED

    # Cancel associated pending matches
    db.query(RequestMatch).filter(
        and_(
            RequestMatch.request_id == request_id,
            RequestMatch.status == MatchStatus.PENDING
        )
    ).update({"status": MatchStatus.REJECTED}) # Marking as rejected/cancelled

    db.commit()
    db.refresh(request)

    # Notify seeker
    notif_service = NotificationService(db)
    notif_service.notify_request_cancelled(request.seeker_id, request)

    return request
