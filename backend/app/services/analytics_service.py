"""National blood supply analytics and district heatmaps."""

from sqlalchemy.orm import Session


def get_national_supply_summary(db: Session):
    raise NotImplementedError


def get_district_heatmap_data(db: Session):
    raise NotImplementedError
