from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut

router = APIRouter()


@router.post("/", response_model=BloodRequestOut, status_code=201)
def create_request(payload: BloodRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # TODO: BloodRequest creation — seeker_id from current_user
    raise NotImplementedError


@router.patch("/{request_id}", response_model=BloodRequestOut)
def update_request(request_id: str, db: Session = Depends(get_db)):
    # TODO: BloodRequest.updateRequest()
    raise NotImplementedError


@router.delete("/{request_id}", status_code=204)
def cancel_request(request_id: str, db: Session = Depends(get_db)):
    # TODO: BloodRequest.cancelRequest()
    raise NotImplementedError


@router.patch("/{request_id}/fulfill", response_model=BloodRequestOut)
def mark_fulfilled(request_id: str, db: Session = Depends(get_db)):
    # TODO: BloodRequest.markFulfilled()
    raise NotImplementedError
