"""Service layer for Lesson operations."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.repositories.lesson_repository import LessonRepository
from app.schemas.lesson import LessonCreate


class LessonService:
    """Business logic for Lesson entities."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = LessonRepository(db)

    def list_lessons(self, unit_id: uuid.UUID) -> list[Lesson]:
        """Return all lessons for a unit."""
        return self._repo.list_by_unit(unit_id)

    def get_lesson(self, lesson_id: uuid.UUID) -> Lesson | None:
        """Return a single lesson by id."""
        return self._repo.get_lesson(lesson_id)

    def create_lesson(
        self, unit_id: uuid.UUID, data: LessonCreate
    ) -> Lesson:
        """Create a new lesson with default status ``draft``."""
        return self._repo.create_lesson(unit_id, data)
