"""Seed script: populates the 7 divisions and 64 districts of Bangladesh.

Run with:
    python -m app.utils.seed_districts
"""

from app.database import SessionLocal
from app.models.division import Division
from app.models.district import District

DIVISIONS = [
    "Dhaka", "Chattogram", "Rajshahi", "Khulna",
    "Barishal", "Sylhet", "Rangpur", "Mymensingh",
]

# TODO: populate the full list of 64 districts, each mapped to its division name.
# Example entry: {"name": "Gazipur", "division": "Dhaka", "lat": 23.9999, "lng": 90.4203}
DISTRICTS: list[dict] = []


def seed():
    db = SessionLocal()
    try:
        division_map = {}
        for name in DIVISIONS:
            division = db.query(Division).filter_by(name=name).first()
            if not division:
                division = Division(name=name)
                db.add(division)
                db.flush()
            division_map[name] = division.division_id
        db.commit()

        for entry in DISTRICTS:
            exists = db.query(District).filter_by(name=entry["name"]).first()
            if not exists:
                db.add(
                    District(
                        name=entry["name"],
                        division_id=division_map[entry["division"]],
                        latitude=entry.get("lat"),
                        longitude=entry.get("lng"),
                    )
                )
        db.commit()
        print(f"Seeded {len(DIVISIONS)} divisions and {len(DISTRICTS)} districts.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
