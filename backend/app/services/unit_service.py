"""Service layer for Unit operations."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.unit import Unit
from app.repositories.unit_repository import UnitRepository
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitService:
    """Business logic for Unit entities."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UnitRepository(db)

    def list_units(self, course_id: uuid.UUID) -> list[Unit]:
        """Return all units for a course."""
        return self._repo.list_by_course(course_id)

    def get_unit(self, unit_id: uuid.UUID) -> Unit | None:
        """Return a single unit by id."""
        return self._repo.get_unit(unit_id)

    def create_unit(
        self, course_id: uuid.UUID, data: UnitCreate
    ) -> Unit:
        """Create a new unit."""
        return self._repo.create_unit(course_id, data)

    def update_unit(
        self, unit_id: uuid.UUID, data: UnitUpdate
    ) -> Unit | None:
        """Update an existing unit."""
        return self._repo.update_unit(unit_id, data)

    def delete_unit(self, unit_id: uuid.UUID) -> bool:
        """Delete a unit.  Returns ``True`` if deleted."""
        return self._repo.delete_unit(unit_id)
