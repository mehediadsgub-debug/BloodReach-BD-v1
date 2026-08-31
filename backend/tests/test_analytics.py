"""
Tests for Analytics and Superadmin Operations
"""
from uuid import uuid4
from app.models import User, UserRole
from app.services import hash_password

def test_analytics_and_admin_management(client, db_session):
    # 1. Create Superadmin user
    admin_user = User(
        user_id=uuid4(),
        full_name="National Superadmin",
        email="superadmin@bloodreach.gov.bd",
        password_hash=hash_password("AdminPass123!"),
        role=UserRole.SUPERADMIN,
        is_active=True
    )
    # Create Regular User
    regular_user = User(
        user_id=uuid4(),
        full_name="Regular Person",
        email="regular@example.com",
        password_hash=hash_password("UserPass123!"),
        role=UserRole.DONOR,
        is_active=True
    )
    db_session.add_all([admin_user, regular_user])
    db_session.commit()

    # Login as Superadmin
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "superadmin@bloodreach.gov.bd", "password": "AdminPass123!", "role": "SUPERADMIN"}
    )
    admin_token = login_res.json()["access_token"]

    # 2. Test Platform Stats
    stats_res = client.get("/api/v1/analytics/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_donors" in stats
    assert "available_donors" in stats
    assert "total_requests" in stats
    assert "districts_covered" in stats
    assert "fulfillment_rate" in stats

    # 3. Test Division Stats
    div_res = client.get("/api/v1/analytics/divisions")
    assert div_res.status_code == 200
    assert len(div_res.json()) >= 1

    # 4. Test Blood Group Stats
    bg_res = client.get("/api/v1/analytics/blood-groups")
    assert bg_res.status_code == 200
    assert len(bg_res.json()) == 8

    # 5. Superadmin lists users
    users_res = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert users_res.status_code == 200
    users = users_res.json()
    assert len(users) >= 2

    # 6. Superadmin deactivates regular user
    deact_res = client.patch(
        f"/api/v1/users/{regular_user.user_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert deact_res.status_code == 200
    assert deact_res.json()["is_active"] is False

    # 7. Superadmin checks audit logs
    logs_res = client.get(
        "/api/v1/analytics/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "USER_DEACTIVATED"
