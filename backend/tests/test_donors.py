"""
Tests for Donor Endpoints (Search, Profile, Availability, Donation History)
"""

def test_donor_search_and_availability(client):
    # Register a donor
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Searchable Donor",
            "email": "searchdonor@example.com",
            "password": "Password123!",
            "role": "DONOR",
            "blood_group": "AB+",
            "district_id": 1
        }
    ).json()
    token = reg["access_token"]

    # Search for AB+ donors
    search_res = client.get("/api/v1/donors/search?blood_group=AB+")
    assert search_res.status_code == 200
    donors = search_res.json()
    assert len(donors) >= 1
    assert donors[0]["blood_group"] == "AB+"

    # Toggle availability to False
    toggle_res = client.patch(
        "/api/v1/users/me/availability?is_available=false",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_available"] is False

    # Search again with is_available_only=True
    search_avail = client.get("/api/v1/donors/search?blood_group=AB+&is_available_only=true")
    assert search_avail.status_code == 200
    assert len(search_avail.json()) == 0


def test_donor_donation_recording_and_history(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "History Donor",
            "email": "historydonor@example.com",
            "password": "Password123!",
            "role": "DONOR",
            "blood_group": "O+",
            "district_id": 1
        }
    ).json()
    token = reg["access_token"]

    # Record a completed donation
    don_res = client.post(
        "/api/v1/donors/me/donations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "donor_id": reg["user_id"],
            "blood_group": "O+",
            "units_donated": 1,
            "notes": "Emergency donation at Dhaka Medical"
        }
    )
    assert don_res.status_code == 201

    # Fetch donation history
    hist_res = client.get(
        "/api/v1/donors/me/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["units_donated"] == 1
