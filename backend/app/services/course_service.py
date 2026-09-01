"""Service layer for Course operations."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.course import Course
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate


class CourseService:
    """Business logic for Course entities."""

    def __init__(self, db: Session) -> None:
        self._repo = CourseRepository(db)

    def list_courses(self) -> list[Course]:
        """Return all courses, newest first."""
        return self._repo.list_courses()

    def get_course(self, course_id: uuid.UUID) -> Course | None:
        """Return a single course by id."""
        return self._repo.get_course(course_id)

    def create_course(self, data: CourseCreate) -> Course:
        """Create a new course."""
        return self._repo.create_course(data)
