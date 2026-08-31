"""
BloodReach BD — WebSocket Endpoint & Real-Time Alerts Tests
"""

import pytest
from starlette.websockets import WebSocketDisconnect
from app.services.auth_service import create_access_token


def test_websocket_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["websocket"] == "enabled"


def test_websocket_invalid_token(client):
    """Connecting with an invalid token should close connection immediately"""
    try:
        with client.websocket_connect("/ws/notifications?token=invalid.jwt.token") as ws:
            pytest.fail("WebSocket should not have connected with invalid token")
    except Exception:
        # Expected closure on unauthorized token
        pass


def test_websocket_valid_token_handshake(client, test_donor):
    """Connecting with a valid JWT token should succeed and respond to ping"""
    token = create_access_token(test_donor.user_id, test_donor.role, test_donor.email)
    with client.websocket_connect(f"/ws/notifications?token={token}") as ws:
        ws.send_text("ping")
        data = ws.receive_text()
        assert data == "pong"
