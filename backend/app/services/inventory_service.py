"""Hospital inventory management and low-stock alerts."""

from sqlalchemy.orm import Session

LOW_STOCK_THRESHOLD = 5  # units


def update_units(inv_id: str, units_available: int, db: Session):
    raise NotImplementedError


def check_low_stock(hospital_id: str, db: Session, threshold: int = LOW_STOCK_THRESHOLD):
    # TODO: query hospital_inventory where units_available < threshold, trigger notification
    raise NotImplementedError
