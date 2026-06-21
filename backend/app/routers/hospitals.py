from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.hospital import HospitalOut, HospitalUpdate

router = APIRouter()


@router.patch("/{hospital_id}", response_model=HospitalOut)
def update_info(hospital_id: str, payload: HospitalUpdate, db: Session = Depends(get_db)):
    # TODO: Hospital.updateInfo()
    raise NotImplementedError


@router.get("/{hospital_id}/inventory")
def get_inventory(hospital_id: str, db: Session = Depends(get_db)):
    # TODO: Hospital.getInventory()
    raise NotImplementedError


@router.get("/{hospital_id}/low-stock")
def get_low_stock(hospital_id: str, db: Session = Depends(get_db)):
    # TODO: Hospital.getLowStock()
    raise NotImplementedError
