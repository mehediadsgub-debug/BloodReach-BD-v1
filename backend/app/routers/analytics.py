from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db

router = APIRouter()


@router.get("/national-supply")
def national_supply_overview(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/district-heatmap")
def district_heatmap(db: Session = Depends(get_db)):
    raise NotImplementedError
