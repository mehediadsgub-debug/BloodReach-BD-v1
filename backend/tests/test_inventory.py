"""
Tests for Hospital Profile and Blood Inventory Management
"""

def test_hospital_inventory_workflow(client):
    # 1. Register Hospital Admin
    hosp_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Dhaka Central Hospital",
            "email": "dhakacentral@hospital.com",
            "password": "Password123!",
            "role": "HOSPITAL_ADMIN",
            "district_id": 1
        }
    ).json()
    hosp_token = hosp_res["access_token"]

    # 2. Fetch inventory (auto-seeds 8 blood groups)
    inv_res = client.get(
        "/api/v1/users/me/hospital-inventory",
        headers={"Authorization": f"Bearer {hosp_token}"}
    )
    assert inv_res.status_code == 200
    inventory = inv_res.json()
    assert len(inventory) == 8

    # 3. Update stock for O+
    update_res = client.put(
        "/api/v1/users/me/hospital-inventory",
        headers={"Authorization": f"Bearer {hosp_token}"},
        json={
            "blood_group": "O+",
            "units_available": 35
        }
    )
    assert update_res.status_code == 200
    assert update_res.json()["units_available"] == 35

    # 4. List public hospitals
    list_res = client.get("/api/v1/hospitals/")
    assert list_res.status_code == 200
    hospitals = list_res.json()
    assert len(hospitals) >= 1
    assert hospitals[0]["name"] == "Dhaka Central Hospital"
