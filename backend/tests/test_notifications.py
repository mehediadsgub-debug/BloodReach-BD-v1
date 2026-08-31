"""
Tests for Notification Endpoints
"""
from uuid import uuid4
from app.models import Notification, NotificationType, User, UserRole
from app.services import hash_password

def test_notification_listing_and_mark_read(client, db_session):
    # Create test user
    user = User(
        user_id=uuid4(),
        full_name="Notif User",
        email="notifuser@example.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.SEEKER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "notifuser@example.com", "password": "Pass123!", "role": "SEEKER"}
    )
    token = login_res.json()["access_token"]

    # Add test notifications
    n1 = Notification(
        notif_id=uuid4(),
        user_id=user.user_id,
        title="Test Alert 1",
        message="Message 1",
        type=NotificationType.SYSTEM,
        is_read=False
    )
    n2 = Notification(
        notif_id=uuid4(),
        user_id=user.user_id,
        title="Test Alert 2",
        message="Message 2",
        type=NotificationType.EMAIL,
        is_read=False
    )
    db_session.add_all([n1, n2])
    db_session.commit()

    # Get notifications
    res = client.get("/api/v1/notifications/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Mark first notification as read
    read_res = client.patch(
        f"/api/v1/notifications/{n1.notif_id}/read",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # Mark all read
    all_read_res = client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert all_read_res.status_code == 200
