from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.donor import DonorOut, DonorAvailabilityUpdate

router = APIRouter()


@router.patch("/{donor_id}/availability", response_model=DonorOut)
def update_availability(donor_id: str, payload: DonorAvailabilityUpdate, db: Session = Depends(get_db)):
    # TODO: Donor.updateAvailability()
    raise NotImplementedError


@router.patch("/{donor_id}/last-donated", response_model=DonorOut)
def update_last_donated(donor_id: str, db: Session = Depends(get_db)):
    # TODO: Donor.updateLastDonated()
    raise NotImplementedError


@router.get("/{donor_id}/donations")
def get_donation_history(donor_id: str, db: Session = Depends(get_db)):
    # TODO: Donor.getDonationHistory()
    raise NotImplementedError
