from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.donation import DonationOut

router = APIRouter()


@router.get("/", response_model=list[DonationOut])
def list_donations(db: Session = Depends(get_db)):
    raise NotImplementedError
