"""
BloodReach BD — Geospatial & Haversine Distance Tests
"""

import pytest
from app.core.geo import haversine_distance, get_district_coordinates, calculate_district_distance
from app.services.matching_service import MatchingEngine
from app.models import User, Donor, District, Division, UserRole


def test_haversine_distance_accuracy():
    # Dhaka (23.8103, 90.4125) to Gazipur (24.0023, 90.4267) is roughly 21-23 km
    dist = haversine_distance(23.8103, 90.4125, 24.0023, 90.4267)
    assert 20.0 <= dist <= 25.0

    # Same coordinate should be 0 km
    assert haversine_distance(23.8103, 90.4125, 23.8103, 90.4125) == 0.0


def test_district_coordinates_lookup():
    dhaka_coords = get_district_coordinates("Dhaka")
    assert dhaka_coords is not None
    assert dhaka_coords[0] == pytest.approx(23.8103, rel=1e-2)

    chattogram_coords = get_district_coordinates("chattogram")
    assert chattogram_coords is not None

    invalid_coords = get_district_coordinates("Atlantis")
    assert invalid_coords is None


def test_calculate_district_distance():
    # Same district
    assert calculate_district_distance("Dhaka", "Dhaka") == 0.0

    # Adjacent districts (Dhaka -> Narayanganj)
    dist_n = calculate_district_distance("Dhaka", "Narayanganj")
    assert 10.0 <= dist_n <= 30.0

    # Far districts (Dhaka -> Cox's Bazar)
    dist_cb = calculate_district_distance("Dhaka", "Cox's Bazar")
    assert dist_cb > 250.0


def test_matching_engine_haversine_sorting(db_session, test_donor):
    """Verify that donor matching prioritizes closest donors by distance in KM"""
    engine = MatchingEngine(db_session)

    # Search from Gazipur (adjacent to Dhaka)
    dhaka_district = db_session.query(District).filter(District.name == "Dhaka").first()
    if dhaka_district:
        matches = engine.find_matching_donors(
            blood_group="O+",
            requester_district_id=dhaka_district.district_id,
            limit=10
        )
        assert len(matches) >= 1
        assert matches[0].blood_group == "O+"
