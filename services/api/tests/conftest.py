"""Shared pytest configuration, database fixtures, and dependency overrides for SahiTol API tests."""
import pytest
from app.main import app
from app.db.session import get_db
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.facility import FacilityUser
from app.db.models.lot import Lot, MediaObject
from app.rate_limiter import phone_limiter, ip_limiter
from tests.test_db import TestingSessionLocal, override_get_db

# Install dependency override globally across all test modules
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_test_state():
    """Clean transactional tables and reset rate limiters before and after every test.

    Only user/collector/lot/session rows are wiped here.  Reference data
    (Facility, Material, Price, Region …) is managed by the relevant test
    module's own module-scoped fixture so that seeding happens once per
    module rather than once per test.
    """
    phone_limiter.reset()
    ip_limiter.reset()
    db = TestingSessionLocal()
    try:
        db.query(MediaObject).delete()
        db.query(Lot).delete()
        db.query(Collector).delete()
        db.query(FacilityUser).delete()
        db.query(AuthSession).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()
    yield
    phone_limiter.reset()
    ip_limiter.reset()
    db = TestingSessionLocal()
    try:
        db.query(MediaObject).delete()
        db.query(Lot).delete()
        db.query(Collector).delete()
        db.query(FacilityUser).delete()
        db.query(AuthSession).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()
