"""
BloodReach BD — Pytest Fixtures & Test Setup
Uses SQLite in-memory database for isolated, fast, automated testing.
"""

import sys
import os
import pytest

# Ensure backend root is in pythonpath
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.models.base import Base
from app.models import Division, District, User, UserRole, Donor, Hospital
from app.core.database import get_db
from main import app
from app.services import hash_password

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables and seed standard test divisions & districts"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed Divisions
    div1 = Division(division_id=1, name="Dhaka", bn_name="ঢাকা")
    div2 = Division(division_id=2, name="Chattogram", bn_name="চট্টগ্রাম")
    div3 = Division(division_id=3, name="Rajshahi", bn_name="রাজশাহী")
    db.add_all([div1, div2, div3])
    db.commit()

    # Seed Districts
    dist1 = District(district_id=1, name="Dhaka", division_id=1)
    dist2 = District(district_id=2, name="Gazipur", division_id=1)
    dist3 = District(district_id=3, name="Chattogram", division_id=2)
    dist4 = District(district_id=4, name="Rajshahi", division_id=3)
    db.add_all([dist1, dist2, dist3, dist4])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a clean transactional database session per test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_donor(db_session):
    """Create a sample active donor user"""
    from app.services.auth_service import hash_password
    user = User(
        full_name="Standard Donor",
        email="donor_fixture@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.DONOR,
        phone="01711000111",
        district_id=1,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    donor = Donor(
        user_id=user.user_id,
        blood_group="O+",
        is_available=True,
        total_donations=3
    )
    db_session.add(donor)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_seeker(db_session):
    """Create a sample active seeker user"""
    from app.services.auth_service import hash_password
    user = User(
        full_name="Emergency Seeker",
        email="seeker_fixture@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.SEEKER,
        phone="01811000222",
        district_id=1,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_hospital_admin(db_session):
    """Create a sample hospital admin and associated hospital"""
    from app.services.auth_service import hash_password
    user = User(
        full_name="Hospital Director",
        email="hospital_fixture@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.HOSPITAL_ADMIN,
        phone="01911000333",
        district_id=1,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    hospital = Hospital(
        name="Dhaka Central Blood Bank",
        admin_user_id=user.user_id,
        district_id=1,
        contact_phone="01911000333",
        is_active=True
    )
    db_session.add(hospital)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def hospital_auth_headers(test_hospital_admin):
    """Create auth headers for test hospital admin"""
    from app.services.auth_service import create_access_token
    token = create_access_token(test_hospital_admin.user_id, test_hospital_admin.role, test_hospital_admin.email)
    return {"Authorization": f"Bearer {token}"}

