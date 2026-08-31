"""
Tests for Location Endpoints (Divisions and Districts)
"""

def test_list_divisions(client):
    response = client.get("/api/v1/locations/divisions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    names = [d["name"] for d in data]
    assert "Dhaka" in names
    assert "Chattogram" in names


def test_list_districts(client):
    response = client.get("/api/v1/locations/districts/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [d["name"] for d in data]
    assert "Dhaka" in names
    assert "Gazipur" in names


def test_list_districts_invalid_division(client):
    response = client.get("/api/v1/locations/districts/9999")
    assert response.status_code == 404
