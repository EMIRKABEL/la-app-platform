"""Pytest configuration and fixtures.

Tests use SQLite in-memory so no PostgreSQL instance is required.
"""

import os
import sys

# Override DATABASE_URL to SQLite before any app imports
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Clear cached settings so the new env var takes effect
from app.core import config  # noqa: E402

config.get_settings.cache_clear()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.session import Base, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables in the in-memory SQLite database."""
    # Use TEXT for JSONB columns in SQLite — create tables with a bind that
    # supports our types loosely
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Return a FastAPI test client."""
    from app.main import app

    with TestClient(app) as c:
        yield c
