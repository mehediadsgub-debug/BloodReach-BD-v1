"""
Tests for Authentication Endpoints (Registration, Login, Token Refresh, Me)
"""

def test_register_donor_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Rahim Donor",
            "email": "donor@example.com",
            "phone": "01711223344",
            "password": "Password123!",
            "role": "DONOR",
            "blood_group": "B+",
            "district_id": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "DONOR"
    assert data["full_name"] == "Rahim Donor"


def test_register_seeker_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Karim Seeker",
            "email": "seeker@example.com",
            "password": "Password123!",
            "role": "SEEKER",
            "district_id": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "SEEKER"


def test_register_duplicate_email_fails(client):
    payload = {
        "full_name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "role": "SEEKER"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]


def test_login_success_and_fail(client):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login Tester",
            "email": "logintester@example.com",
            "password": "CorrectPassword123",
            "role": "SEEKER"
        }
    )

    # Valid Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "logintester@example.com",
            "password": "CorrectPassword123",
            "role": "SEEKER"
        }
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # Invalid Password
    bad_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "logintester@example.com",
            "password": "WrongPassword",
            "role": "SEEKER"
        }
    )
    assert bad_login.status_code == 401

    # Wrong Role
    wrong_role = client.post(
        "/api/v1/auth/login",
        json={
            "email": "logintester@example.com",
            "password": "CorrectPassword123",
            "role": "DONOR"
        }
    )
    assert wrong_role.status_code == 403


def test_login_with_phone(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Phone Login Tester",
            "email": "phonelogin@example.com",
            "phone": "01710000000",
            "password": "CorrectPassword123",
            "role": "SEEKER"
        }
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "01710000000",
            "password": "CorrectPassword123",
            "role": "SEEKER"
        }
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_token_refresh(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Refresh Tester",
            "email": "refreshtester@example.com",
            "password": "Password123!",
            "role": "SEEKER"
        }
    ).json()

    refresh_token = reg["refresh_token"]
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()


def test_register_donor_with_district_name_and_formatted_phone(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "District Name Donor",
            "email": "districtdonor@example.com",
            "phone": "01711-998877",
            "password": "Password123!",
            "role": "DONOR",
            "blood_group": "O+",
            "district": "Dhaka",
            "division": "Dhaka"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "DONOR"
    assert data["full_name"] == "District Name Donor"


def test_register_hospital_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "City General Hospital",
            "email": "cityhospital@example.com",
            "phone": "+880 1711 556677",
            "password": "Password123!",
            "role": "HOSPITAL",
            "district": "Dhaka"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "HOSPITAL_ADMIN"
    assert "access_token" in data


def test_register_with_phone_only(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Phone Only User",
            "phone": "01811-334455",
            "password": "Password123!",
            "role": "SEEKER"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "SEEKER"
    assert data["full_name"] == "Phone Only User"


