from decimal import Decimal

from pydantic import BaseModel


class DivisionOut(BaseModel):
    division_id: int
    name: str

    class Config:
        from_attributes = True


class DistrictOut(BaseModel):
    district_id: int
    division_id: int
    name: str
    latitude: Decimal | None
    longitude: Decimal | None

    class Config:
        from_attributes = True
