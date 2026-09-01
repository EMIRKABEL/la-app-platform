"""Repository for Unit database operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitRepository:
    """Data-access layer for Unit entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_course(self, course_id: uuid.UUID) -> list[Unit]:
        """Return all units for a course, ordered by number."""
        stmt = (
            select(Unit)
            .where(Unit.course_id == course_id)
            .order_by(Unit.number)
        )
        return list(self._db.scalars(stmt).all())

    def get_unit(self, unit_id: uuid.UUID) -> Unit | None:
        """Return a single unit by id, or ``None``."""
        stmt = select(Unit).where(Unit.id == unit_id)
        return self._db.scalars(stmt).first()

    def create_unit(
        self, course_id: uuid.UUID, data: UnitCreate
    ) -> Unit:
        """Create and return a new unit."""
        unit = Unit(
            course_id=course_id,
            number=data.number,
            title=data.title,
        )
        self._db.add(unit)
        self._db.commit()
        self._db.refresh(unit)
        return unit

    def update_unit(
        self, unit_id: uuid.UUID, data: UnitUpdate
    ) -> Unit | None:
        """Update an existing unit.  Returns ``None`` if not found."""
        unit = self.get_unit(unit_id)
        if unit is None:
            return None
        unit.number = data.number
        unit.title = data.title
        self._db.commit()
        self._db.refresh(unit)
        return unit

    def delete_unit(self, unit_id: uuid.UUID) -> bool:
        """Delete a unit.  Returns ``True`` if deleted, ``False`` if missing."""
        unit = self.get_unit(unit_id)
        if unit is None:
            return False
        self._db.delete(unit)
        self._db.commit()
        return True
