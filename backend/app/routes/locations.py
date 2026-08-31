"""
BloodReach BD — Location Routes
Divisions & districts lookup (used by the registration form).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Division, District
from app.schemas import DivisionResponse, DistrictResponse

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])


@router.get("/divisions", response_model=list[DivisionResponse])
def list_divisions(db: Session = Depends(get_db)):
    """List all divisions (Bangladesh has 8)"""
    return db.query(Division).order_by(Division.division_id).all()


@router.get("/districts/{division_id}", response_model=list[DistrictResponse])
def list_districts(division_id: int, db: Session = Depends(get_db)):
    """List all districts under a given division"""
    division = db.query(Division).filter(Division.division_id == division_id).first()
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Division not found"
        )
    return (
        db.query(District)
        .filter(District.division_id == division_id)
        .order_by(District.district_id)
        .all()
    )
