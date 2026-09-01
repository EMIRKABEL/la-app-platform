"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core import settings


def _get_database_url() -> str:
    """Return the database URL.

    If the environment overrides ``DATABASE_URL`` to a SQLite URL (for
    testing), we use it as-is.  Otherwise the configured PostgreSQL URL
    is used.
    """
    url = settings.DATABASE_URL
    return url


engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


def get_db():
    """Yield a database session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
