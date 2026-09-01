"""Shared mixins for ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid as SAUuid


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID primary key column.

    Uses ``sqlalchemy.types.Uuid`` which is database-agnostic and works
    with both PostgreSQL (native UUID) and SQLite (stores as string).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        SAUuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class TimestampMixin:
    """Mixin providing ``created_at`` and ``updated_at`` timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=utcnow,
        nullable=False,
    )
