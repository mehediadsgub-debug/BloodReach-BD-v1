"""
BloodReach BD — Analytics & Audit Routes
National health metrics, division heatmaps, blood group distribution, and audit trails.
"""

from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.core.dependencies import require_superadmin, get_current_active_user
from app.models import (
    User, UserRole, Donor, Hospital, HospitalInventory,
    BloodRequest, RequestStatus, UrgencyLevel, Division, District,
    Donation, AuditLog
)
from app.schemas import (
    DashboardStats,
    DivisionStats,
    BloodGroupStats,
    AuditLogResponse
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated platform statistics across Bangladesh:
    Donors, Seekers, Hospitals, Total Requests, Pending, Critical, and Fulfilled.
    """
    total_donors = db.query(func.count(Donor.donor_id)).scalar() or 0
    available_donors = (
        db.query(func.count(Donor.donor_id))
        .join(User, Donor.user_id == User.user_id)
        .filter(Donor.is_available == True, User.is_active == True)
        .scalar() or 0
    )
    total_seekers = db.query(func.count(User.user_id)).filter(User.role == UserRole.SEEKER).scalar() or 0
    total_hospitals = db.query(func.count(Hospital.hospital_id)).scalar() or 0
    total_requests = db.query(func.count(BloodRequest.request_id)).scalar() or 0
    districts_covered = db.query(func.count(District.district_id)).scalar() or 0
    fulfilled_requests = (
        db.query(func.count(BloodRequest.request_id))
        .filter(BloodRequest.status == RequestStatus.FULFILLED)
        .scalar() or 0
    )
    fulfillment_rate = round((fulfilled_requests / total_requests) * 100, 2) if total_requests else 0.0

    pending_requests = (
        db.query(func.count(BloodRequest.request_id))
        .filter(BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.IN_PROGRESS]))
        .scalar() or 0
    )

    critical_requests = (
        db.query(func.count(BloodRequest.request_id))
        .filter(
            BloodRequest.urgency_level == UrgencyLevel.CRITICAL,
            BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.IN_PROGRESS])
        )
        .scalar() or 0
    )

    fulfilled_today = (
        db.query(func.count(Donation.donation_id))
        .filter(Donation.donation_date == date.today())
        .scalar() or 0
    )

    low_stock_alerts = (
        db.query(func.count(HospitalInventory.inv_id))
        .filter(HospitalInventory.units_available <= HospitalInventory.low_stock_alert)
        .scalar() or 0
    )

    return DashboardStats(
        total_donors=total_donors,
        available_donors=available_donors,
        total_seekers=total_seekers,
        total_hospitals=total_hospitals,
        total_requests=total_requests,
        districts_covered=districts_covered,
        fulfillment_rate=fulfillment_rate,
        pending_requests=pending_requests,
        critical_requests=critical_requests,
        fulfilled_today=fulfilled_today,
        low_stock_alerts=low_stock_alerts
    )


@router.get("/divisions", response_model=List[DivisionStats])
def get_division_stats(db: Session = Depends(get_db)):
    """
    Get regional breakdown of donors, seekers, and hospitals by 8 divisions.
    """
    divisions = db.query(Division).order_by(Division.division_id).all()
    results = []

    for div in divisions:
        # Donors in this division
        donors_cnt = (
            db.query(func.count(Donor.donor_id))
            .join(User, Donor.user_id == User.user_id)
            .join(District, User.district_id == District.district_id)
            .filter(District.division_id == div.division_id)
            .scalar() or 0
        )

        # Seekers in this division
        seekers_cnt = (
            db.query(func.count(User.user_id))
            .join(District, User.district_id == District.district_id)
            .filter(User.role == UserRole.SEEKER, District.division_id == div.division_id)
            .scalar() or 0
        )

        # Hospitals in this division
        hospitals_cnt = (
            db.query(func.count(Hospital.hospital_id))
            .join(District, Hospital.district_id == District.district_id)
            .filter(District.division_id == div.division_id)
            .scalar() or 0
        )

        # Calculate coverage label
        if donors_cnt >= 20:
            coverage = "High"
        elif donors_cnt >= 5:
            coverage = "Medium"
        elif donors_cnt >= 1:
            coverage = "Low"
        else:
            coverage = "Very Low"

        results.append(
            DivisionStats(
                division=div.name,
                donors=donors_cnt,
                seekers=seekers_cnt,
                hospitals=hospitals_cnt,
                coverage=coverage
            )
        )

    return results


@router.get("/blood-groups", response_model=List[BloodGroupStats])
def get_blood_group_stats(db: Session = Depends(get_db)):
    """
    Get supply and demand metrics for all 8 blood groups.
    """
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    results = []

    for bg in blood_groups:
        avail_donors = (
            db.query(func.count(Donor.donor_id))
            .filter(Donor.blood_group == bg, Donor.is_available == True)
            .scalar() or 0
        )

        pending_reqs = (
            db.query(func.count(BloodRequest.request_id))
            .filter(
                BloodRequest.blood_group == bg,
                BloodRequest.status.in_([RequestStatus.OPEN, RequestStatus.IN_PROGRESS])
            )
            .scalar() or 0
        )

        stock_units = (
            db.query(func.sum(HospitalInventory.units_available))
            .filter(HospitalInventory.blood_group == bg)
            .scalar() or 0
        )

        results.append(
            BloodGroupStats(
                blood_group=bg,
                available_donors=avail_donors,
                pending_requests=pending_reqs,
                hospital_stock=int(stock_units)
            )
        )

    return results


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """Get system audit logs (Superadmin only)"""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
