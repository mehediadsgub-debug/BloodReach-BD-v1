"""Business logic for donor profile management."""

from sqlalchemy.orm import Session


def toggle_availability(donor_id: str, is_available: bool, db: Session):
    raise NotImplementedError


def update_last_donated(donor_id: str, db: Session):
    raise NotImplementedError


def get_donation_history(donor_id: str, db: Session):
    raise NotImplementedError
