"""Repository for Lesson database operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.enums import LessonStatus
from app.schemas.lesson import LessonCreate


class LessonRepository:
    """Data-access layer for Lesson entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_unit(self, unit_id: uuid.UUID) -> list[Lesson]:
        """Return all lessons for a unit, ordered by number."""
        stmt = (
            select(Lesson)
            .where(Lesson.unit_id == unit_id)
            .order_by(Lesson.number)
        )
        return list(self._db.scalars(stmt).all())

    def get_lesson(self, lesson_id: uuid.UUID) -> Lesson | None:
        """Return a single lesson by id, or ``None``."""
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        return self._db.scalars(stmt).first()

    def create_lesson(
        self, unit_id: uuid.UUID, data: LessonCreate
    ) -> Lesson:
        """Create and return a new lesson with default status ``draft``."""
        lesson = Lesson(
            unit_id=unit_id,
            number=data.number,
            title=data.title,
            status=LessonStatus.draft,
        )
        self._db.add(lesson)
        self._db.commit()
        self._db.refresh(lesson)
        return lesson
