from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.hospital_inventory import HospitalInventoryOut, InventoryUnitsUpdate

router = APIRouter()


@router.patch("/{inv_id}/units", response_model=HospitalInventoryOut)
def update_units(inv_id: str, payload: InventoryUnitsUpdate, db: Session = Depends(get_db)):
    # TODO: HospitalInventory.updateUnits() — also triggers low-stock alert check
    raise NotImplementedError
