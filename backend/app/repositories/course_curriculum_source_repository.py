"""Repository for CourseCurriculumSource database operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course_curriculum_source import CourseCurriculumSource
from app.models.enums import CurriculumProcessingStatus


class CourseCurriculumSourceRepository:
    """Data-access layer for CourseCurriculumSource entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_course(
        self, course_id: uuid.UUID
    ) -> list[CourseCurriculumSource]:
        """Return all curriculum sources for a course, newest first."""
        stmt = (
            select(CourseCurriculumSource)
            .where(CourseCurriculumSource.course_id == course_id)
            .order_by(CourseCurriculumSource.uploaded_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get_by_id(
        self, curriculum_id: uuid.UUID
    ) -> CourseCurriculumSource | None:
        """Return a single course curriculum source by id, or ``None``."""
        stmt = select(CourseCurriculumSource).where(
            CourseCurriculumSource.id == curriculum_id
        )
        return self._db.scalars(stmt).first()

    def update_status(
        self,
        curriculum_id: uuid.UUID,
        status: CurriculumProcessingStatus,
    ) -> CourseCurriculumSource | None:
        """Update the processing status of a course curriculum source."""
        record = self.get_by_id(curriculum_id)
        if record is None:
            return None
        record.processing_status = status
        self._db.commit()
        self._db.refresh(record)
        return record

    def save_extraction(
        self,
        curriculum_id: uuid.UUID,
        extracted_data: dict[str, Any],
        status: CurriculumProcessingStatus = CurriculumProcessingStatus.completed,
    ) -> CourseCurriculumSource | None:
        """Save extracted curriculum data and update status/timestamp."""
        record = self.get_by_id(curriculum_id)
        if record is None:
            return None
        record.extracted_data = extracted_data
        record.extracted_at = datetime.now(timezone.utc)
        record.processing_status = status
        self._db.commit()
        self._db.refresh(record)
        return record

    def create(
        self,
        *,
        course_id: uuid.UUID,
        original_filename: str,
        file_type: str,
        storage_path: str,
    ) -> CourseCurriculumSource:
        """Create and return a new course curriculum source record."""
        record = CourseCurriculumSource(
            course_id=course_id,
            original_filename=original_filename,
            file_type=file_type,
            storage_path=storage_path,
            processing_status=CurriculumProcessingStatus.pending,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record
