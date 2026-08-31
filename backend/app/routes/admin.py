"""
BloodReach BD — Admin Verification & Anti-Fraud Management Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import (
    User,
    UserRole,
    Donor,
    BloodRequest,
    RequestMatch,
    MatchStatus,
    RequestStatus,
    VerificationStatus,
    District,
    Division,
    Hospital
)
from app.schemas import AdminVerifyRequest
from app.services.matching_service import MatchingEngine
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Verification & Anti-Fraud"])


def require_superadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """Ensure current user is SUPERADMIN or ADMIN"""
    if current_user.role not in [UserRole.SUPERADMIN, "ADMIN", "SUPERADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to platform Superadmins only."
        )
    return current_user


@router.get("/verification-queue")
def get_verification_queue(
    status_filter: Optional[str] = Query("ALL", description="Filter by ALL, PENDING, APPROVED, FLAGGED_FRAUD, REJECTED"),
    blood_group: Optional[str] = Query(None),
    district_id: Optional[int] = Query(None),
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Fetch all blood requests with NID anti-fraud verification details"""
    query = db.query(BloodRequest).order_by(desc(BloodRequest.created_at))

    if status_filter and status_filter.upper() != "ALL":
        if status_filter.upper() == "PENDING":
            query = query.filter(BloodRequest.verification_status == VerificationStatus.PENDING_VERIFICATION)
        elif status_filter.upper() == "APPROVED":
            query = query.filter(BloodRequest.verification_status == VerificationStatus.APPROVED)
        elif status_filter.upper() in ["FLAGGED_FRAUD", "FRAUD"]:
            query = query.filter(BloodRequest.verification_status == VerificationStatus.FLAGGED_FRAUD)
        elif status_filter.upper() == "REJECTED":
            query = query.filter(BloodRequest.verification_status == VerificationStatus.REJECTED)

    if blood_group:
        query = query.filter(BloodRequest.blood_group == blood_group.strip())

    if district_id:
        query = query.filter(BloodRequest.district_id == district_id)

    requests = query.limit(100).all()

    results = []
    for req in requests:
        seeker = req.seeker
        district_name = req.district.name if req.district else "Unknown"
        division_name = req.district.division.name if req.district and req.district.division else "Unknown"

        results.append({
            "request_id": str(req.request_id),
            "seeker_id": str(req.seeker_id) if req.seeker_id else None,
            "seeker_name": seeker.full_name if seeker else (req.patient_name or "Anonymous Seeker"),
            "seeker_email": seeker.email if seeker else None,
            "seeker_phone": seeker.phone if seeker else req.contact_phone,
            "blood_group": req.blood_group,
            "units_needed": req.units_needed,
            "urgency_level": req.urgency_level.value if hasattr(req.urgency_level, "value") else str(req.urgency_level),
            "status": req.status.value if hasattr(req.status, "value") else str(req.status),
            "verification_status": req.verification_status.value if hasattr(req.verification_status, "value") else str(req.verification_status),
            "nid_number": req.nid_number,
            "nid_name": req.nid_name or (seeker.full_name if seeker else None),
            "nid_dob": req.nid_dob,
            "nid_image_url": req.nid_image_url,
            "hospital_name": req.hospital_name or (req.hospital.name if req.hospital else "Not Specified"),
            "hospital_cabin": req.hospital_cabin,
            "patient_name": req.patient_name,
            "patient_condition": req.patient_condition,
            "district": district_name,
            "division": division_name,
            "admin_notes": req.admin_notes,
            "verified_at": req.verified_at.isoformat() if req.verified_at else None,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        })

    return results


@router.post("/requests/{request_id}/verify")
def verify_blood_request(
    request_id: UUID,
    payload: AdminVerifyRequest,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Admin action to approve, reject, or flag a blood request as fraud"""
    req = db.query(BloodRequest).filter(BloodRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found"
        )

    action = payload.action.upper()
    notif_service = NotificationService(db)

    if action == "APPROVE":
        req.verification_status = VerificationStatus.APPROVED
        req.status = RequestStatus.OPEN
        req.verified_at = datetime.utcnow()
        req.verified_by_id = current_user.user_id
        req.admin_notes = payload.admin_notes or "NID Card & Seeker Information Verified by Admin"

        db.commit()
        db.refresh(req)

        # Trigger Donor Matching Engine now that it is officially verified!
        matches_count = 0
        try:
            engine = MatchingEngine(db)
            engine.auto_match_request(req)

            pending_matches = db.query(RequestMatch).filter(
                and_(
                    RequestMatch.request_id == req.request_id,
                    RequestMatch.status == MatchStatus.PENDING
                )
            ).all()
            matches_count = len(pending_matches)

            for match in pending_matches:
                donor = db.query(Donor).filter(Donor.donor_id == match.donor_id).first()
                if donor and donor.user_id:
                    notif_service.notify_donor_match(donor.user_id, req, match.match_id)
        except Exception as e:
            print(f"[WARN] Error running matching engine on approved request: {e}")

        return {
            "success": True,
            "message": f"Request approved successfully! Alerted {matches_count} matching donors in the region.",
            "request_id": str(req.request_id),
            "verification_status": req.verification_status.value,
            "matches_generated": matches_count
        }

    elif action in ["REJECT", "FLAG_FRAUD"]:
        new_status = VerificationStatus.FLAGGED_FRAUD if action == "FLAG_FRAUD" else VerificationStatus.REJECTED
        req.verification_status = new_status
        req.status = RequestStatus.CANCELLED
        req.verified_at = datetime.utcnow()
        req.verified_by_id = current_user.user_id
        req.admin_notes = payload.admin_notes or ("Flagged as potential fraudulent NID / Fake Request" if action == "FLAG_FRAUD" else "Rejected by Admin")

        db.commit()
        db.refresh(req)

        return {
            "success": True,
            "message": f"Request marked as {new_status.value}. Donors will not be contacted.",
            "request_id": str(req.request_id),
            "verification_status": req.verification_status.value
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action}. Must be APPROVE, REJECT, or FLAG_FRAUD."
        )


@router.get("/verification-stats")
def get_verification_stats(
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Return live metrics for NID verification anti-fraud queue"""
    total = db.query(BloodRequest).count()
    pending = db.query(BloodRequest).filter(BloodRequest.verification_status == VerificationStatus.PENDING_VERIFICATION).count()
    approved = db.query(BloodRequest).filter(BloodRequest.verification_status == VerificationStatus.APPROVED).count()
    fraud = db.query(BloodRequest).filter(BloodRequest.verification_status == VerificationStatus.FLAGGED_FRAUD).count()
    rejected = db.query(BloodRequest).filter(BloodRequest.verification_status == VerificationStatus.REJECTED).count()

    total_donors = db.query(Donor).count()

    return {
        "total_requests": total,
        "pending_queue": pending,
        "approved_requests": approved,
        "flagged_fraud": fraud,
        "rejected_requests": rejected,
        "donors_protected": total_donors
    }
