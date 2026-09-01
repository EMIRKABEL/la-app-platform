"""Pytest configuration and fixtures.

Tests use SQLite in-memory so no PostgreSQL instance is required.
A ``StaticPool`` ensures all sessions share the same single in-memory
database connection.
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
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.session import Base  # noqa: E402
import app.db.session as db_session_module  # noqa: E402

# Recreate the engine with StaticPool so all sessions share one connection
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Patch the module-level engine and SessionLocal so the app uses the
# same in-memory database during tests
db_session_module.engine = test_engine
db_session_module.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def _override_get_db():
    """Yield a session from the shared test engine."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables in the in-memory SQLite database."""
    # Ensure all models are imported so Base.metadata knows about them
    import app.models  # noqa: F401 — side-effect import

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Delete all rows before each test to keep tests isolated."""
    from app.models import (  # noqa: F401 — side-effect import
        Activity,
        Asset,
        Course,
        CurriculumSource,
        Lesson,
        LessonObjective,
        LessonVersion,
        Unit,
    )

    # Delete in dependency order to respect FK constraints
    tables = [
        LessonVersion,
        Activity,
        LessonObjective,
        CurriculumSource,
        Lesson,
        Unit,
        Course,
        Asset,
    ]
    db = TestingSessionLocal()
    try:
        for table in tables:
            db.query(table).delete()
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    """Return a FastAPI test client with the DB dependency overridden."""
    from app.main import app
    from app.db.session import get_db

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
