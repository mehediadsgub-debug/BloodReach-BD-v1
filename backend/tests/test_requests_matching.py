"""
Tests for Blood Request Lifecycle and Automatic Matching Engine
"""

def test_request_lifecycle_and_matching(client):
    # 1. Register a Donor (A+, District 1)
    donor_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Matched Donor",
            "email": "matcheddonor@example.com",
            "password": "Password123!",
            "role": "DONOR",
            "blood_group": "A+",
            "district_id": 1
        }
    ).json()
    donor_token = donor_res["access_token"]

    # 2. Register a Seeker (District 1)
    seeker_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Urgent Seeker",
            "email": "urgentseeker@example.com",
            "password": "Password123!",
            "role": "SEEKER",
            "district_id": 1
        }
    ).json()
    seeker_token = seeker_res["access_token"]

    # 3. Seeker posts a blood request
    req_res = client.post(
        "/api/v1/requests/",
        headers={"Authorization": f"Bearer {seeker_token}"},
        json={
            "blood_group": "A+",
            "units_needed": 1,
            "district_id": 1,
            "urgency_level": "CRITICAL",
            "patient_name": "Emergency Patient",
            "patient_condition": "Accident trauma"
        }
    )
    assert req_res.status_code == 201
    request_data = req_res.json()
    request_id = request_data["request_id"]
    assert request_data["urgency_level"] == "CRITICAL"

    # 4. Donor checks pending matches
    pending_res = client.get(
        "/api/v1/requests/matches/pending",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert pending_res.status_code == 200
    matches = pending_res.json()
    assert len(matches) >= 1
    match_id = matches[0]["match_id"]

    # 5. Donor accepts match
    respond_res = client.post(
        f"/api/v1/requests/matches/{match_id}/respond?accept=true&notes=On+my+way",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert respond_res.status_code == 200
    assert respond_res.json()["status"] == "ACCEPTED"

    # 6. Seeker views matches for the request
    seeker_matches = client.get(
        f"/api/v1/requests/{request_id}/matches",
        headers={"Authorization": f"Bearer {seeker_token}"}
    )
    assert seeker_matches.status_code == 200
    assert len(seeker_matches.json()) >= 1


def test_cancel_blood_request(client):
    # Register Seeker
    seeker_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Cancel Seeker",
            "email": "cancelseeker@example.com",
            "password": "Password123!",
            "role": "SEEKER",
            "district_id": 1
        }
    ).json()
    seeker_token = seeker_res["access_token"]

    # Create Request
    req_res = client.post(
        "/api/v1/requests/",
        headers={"Authorization": f"Bearer {seeker_token}"},
        json={
            "blood_group": "B+",
            "units_needed": 2,
            "district_id": 1,
            "urgency_level": "NORMAL"
        }
    ).json()
    request_id = req_res["request_id"]

    # Cancel Request
    del_res = client.delete(
        f"/api/v1/requests/{request_id}",
        headers={"Authorization": f"Bearer {seeker_token}"}
    )
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "CANCELLED"
