"""Custom SQLAlchemy types for database portability.

These types use PostgreSQL-native types (JSONB, UUID) when running on
PostgreSQL, and fall back to SQLite-compatible equivalents for local
development and testing.
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator


class JSONBType(TypeDecorator):
    """A JSON column type that uses JSONB on PostgreSQL and JSON elsewhere.

    This keeps the application portable: production on PostgreSQL benefits
    from JSONB indexing and operators, while tests run on SQLite without
    issues.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
