from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db

router = APIRouter()


@router.get("/search")
def search_donors(district_id: int, blood_group: str, db: Session = Depends(get_db)):
    # TODO: geo-filter donors by district/division + blood group, proximity ranking
    raise NotImplementedError


@router.post("/{request_id}/notify")
def notify_donors(request_id: str, db: Session = Depends(get_db)):
    # TODO: create RequestMatch rows + dispatch notifications
    raise NotImplementedError


@router.patch("/matches/{match_id}/accept")
def accept_match(match_id: str, db: Session = Depends(get_db)):
    # TODO: RequestMatch.acceptMatch()
    raise NotImplementedError


@router.patch("/matches/{match_id}/decline")
def decline_match(match_id: str, db: Session = Depends(get_db)):
    # TODO: RequestMatch.declineMatch()
    raise NotImplementedError


@router.patch("/matches/{match_id}/fulfill")
def fulfill_match(match_id: str, db: Session = Depends(get_db)):
    # TODO: RequestMatch.markFulfilled() -> triggers Donation.recordDonation()
    raise NotImplementedError
