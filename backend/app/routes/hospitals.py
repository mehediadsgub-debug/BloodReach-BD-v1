"""
BloodReach BD — Hospital Routes
Hospital listing, public profiles, and inventory lookup.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.models import Hospital, HospitalInventory, District, Division
from app.schemas import HospitalResponse, InventoryResponse

router = APIRouter(prefix="/api/v1/hospitals", tags=["Hospitals"])


@router.get("/", response_model=List[HospitalResponse])
def list_hospitals(
    division_id: Optional[int] = Query(None, description="Filter by division ID"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    query: Optional[str] = Query(None, description="Search by hospital name"),
    is_active: bool = Query(True, description="Only active hospitals"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List hospitals with optional location and name filters"""
    stmt = db.query(Hospital)
    if is_active:
        stmt = stmt.filter(Hospital.is_active == True)

    if district_id:
        stmt = stmt.filter(Hospital.district_id == district_id)
    elif division_id:
        stmt = stmt.join(District, Hospital.district_id == District.district_id).filter(
            District.division_id == division_id
        )

    if query:
        stmt = stmt.filter(Hospital.name.ilike(f"%{query.strip()}%"))

    return stmt.order_by(Hospital.name).limit(limit).all()


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db)
):
    """Get hospital profile details"""
    hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    return hospital


@router.get("/{hospital_id}/inventory", response_model=List[InventoryResponse])
def get_hospital_inventory(
    hospital_id: UUID,
    db: Session = Depends(get_db)
):
    """Get blood stock inventory for a hospital"""
    hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    return hospital.inventory
