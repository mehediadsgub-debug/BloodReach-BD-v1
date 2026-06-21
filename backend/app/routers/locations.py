from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.location import DivisionOut, DistrictOut

router = APIRouter()


@router.get("/divisions", response_model=list[DivisionOut])
def get_all_divisions(db: Session = Depends(get_db)):
    # TODO: Division.getAllDivisions()
    raise NotImplementedError


@router.get("/divisions/{division_id}", response_model=DivisionOut)
def get_division_by_id(division_id: int, db: Session = Depends(get_db)):
    # TODO: Division.getDivisionById()
    raise NotImplementedError


@router.get("/districts", response_model=list[DistrictOut])
def get_all_districts(db: Session = Depends(get_db)):
    # TODO: District.getAllDistricts()
    raise NotImplementedError


@router.get("/districts/{district_id}", response_model=DistrictOut)
def get_district_by_id(district_id: int, db: Session = Depends(get_db)):
    # TODO: District.getDistrictById()
    raise NotImplementedError
