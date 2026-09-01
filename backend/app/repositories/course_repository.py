"""Repository for Course database operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CourseRepository:
    """Data-access layer for Course entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_courses(self) -> list[Course]:
        """Return all courses, newest first."""
        stmt = select(Course).order_by(
            desc(Course.created_at),
            desc(Course.id),
        )
        return list(self._db.scalars(stmt).all())

    def get_course(self, course_id: uuid.UUID) -> Course | None:
        """Return a single course by id, or ``None``."""
        stmt = select(Course).where(Course.id == course_id)
        return self._db.scalars(stmt).first()

    def create_course(self, data: CourseCreate) -> Course:
        """Create and return a new course."""
        course = Course(name=data.name, description=data.description)
        self._db.add(course)
        self._db.commit()
        self._db.refresh(course)
        return course

    def update_course(
        self, course_id: uuid.UUID, data: CourseUpdate
    ) -> Course | None:
        """Update an existing course.  Returns ``None`` if not found."""
        course = self.get_course(course_id)
        if course is None:
            return None
        course.name = data.name
        course.description = data.description
        self._db.commit()
        self._db.refresh(course)
        return course

    def delete_course(self, course_id: uuid.UUID) -> bool:
        """Delete a course.  Returns ``True`` if deleted, ``False`` if missing."""
        course = self.get_course(course_id)
        if course is None:
            return False
        self._db.delete(course)
        self._db.commit()
        return True
