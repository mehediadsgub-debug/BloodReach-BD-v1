"""Location-based donor matching and proximity ranking."""

from sqlalchemy.orm import Session


def find_matching_donors(district_id: int, blood_group: str, db: Session):
    # TODO: filter Donor by blood_group + is_available, join District,
    # rank by same-district first, then same-division, then distance (lat/lng).
    raise NotImplementedError


def create_match(request_id: str, donor_id: str, db: Session):
    raise NotImplementedError
