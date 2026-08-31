"""
BloodReach BD — Concurrency & Race Condition Protection Tests
"""

import pytest
from app.models import BloodRequest, RequestMatch, MatchStatus, RequestStatus, HospitalInventory
from app.services.matching_service import MatchingEngine


def test_request_overfulfillment_protection(db_session, test_seeker, test_donor):
    """Test that once a request is fulfilled, subsequent acceptances are blocked or gracefully rejected"""
    # Create a 1-unit blood request
    req = BloodRequest(
        seeker_id=test_seeker.user_id,
        patient_name="Emergency Patient",
        blood_group="O+",
        units_needed=1,
        status=RequestStatus.OPEN
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    # Create match
    match1 = RequestMatch(
        request_id=req.request_id,
        donor_id=test_donor.donor_profile.donor_id,
        status=MatchStatus.PENDING
    )
    db_session.add(match1)
    db_session.commit()
    db_session.refresh(match1)

    engine = MatchingEngine(db_session)

    # First donor accepts
    responded_match = engine.respond_to_match(
        match_id=match1.match_id,
        donor_id=test_donor.donor_profile.donor_id,
        accept=True
    )
    assert responded_match.status == MatchStatus.ACCEPTED
    assert req.status == RequestStatus.FULFILLED

    # Create second donor
    from app.models import User, UserRole, Donor
    from app.services.auth_service import hash_password
    user2 = User(
        full_name="Second Donor",
        email="donor2_concurrency@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.DONOR,
        phone="01711999888",
        district_id=1,
        is_active=True
    )
    db_session.add(user2)
    db_session.flush()

    donor2 = Donor(
        user_id=user2.user_id,
        blood_group="O+",
        is_available=True
    )
    db_session.add(donor2)
    db_session.commit()

    # Create match for donor 2 after request has already been fulfilled by donor 1
    match2 = RequestMatch(
        request_id=req.request_id,
        donor_id=donor2.donor_id,
        status=MatchStatus.PENDING
    )
    db_session.add(match2)
    db_session.commit()

    # Second acceptance must raise ValueError due to concurrency protection
    with pytest.raises(ValueError) as excinfo:
        engine.respond_to_match(
            match_id=match2.match_id,
            donor_id=donor2.donor_id,
            accept=True
        )
    assert "already fulfilled" in str(excinfo.value).lower()


def test_atomic_inventory_deduction(client, test_hospital_admin, hospital_auth_headers):
    """Test atomic inventory adjustment API prevents negative balance"""
    # Initialize inventory with 5 units of A+
    res = client.put(
        "/api/v1/users/me/hospital-inventory",
        json={"blood_group": "A+", "units_available": 5},
        headers=hospital_auth_headers
    )
    assert res.status_code == 200

    # Safely deduct 2 units
    adjust_res = client.post(
        "/api/v1/users/me/hospital-inventory/adjust",
        json={"blood_group": "A+", "delta_units": -2},
        headers=hospital_auth_headers
    )
    assert adjust_res.status_code == 200
    assert adjust_res.json()["units_available"] == 3

    # Attempt to deduct 10 units (exceeding stock of 3) -> Must fail with 400 Bad Request
    fail_res = client.post(
        "/api/v1/users/me/hospital-inventory/adjust",
        json={"blood_group": "A+", "delta_units": -10},
        headers=hospital_auth_headers
    )
    assert fail_res.status_code == 400
    assert "insufficient" in fail_res.json()["detail"].lower()
