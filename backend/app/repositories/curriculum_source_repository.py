"""Repository for CurriculumSource database operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum_source import CurriculumSource
from app.models.enums import CurriculumProcessingStatus


class CurriculumSourceRepository:
    """Data-access layer for CurriculumSource entities."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_lesson(
        self, lesson_id: uuid.UUID
    ) -> list[CurriculumSource]:
        """Return all curriculum sources for a lesson, newest first."""
        stmt = (
            select(CurriculumSource)
            .where(CurriculumSource.lesson_id == lesson_id)
            .order_by(CurriculumSource.uploaded_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get_by_id(self, curriculum_id: uuid.UUID) -> CurriculumSource | None:
        """Return a single curriculum source by id, or ``None``."""
        stmt = select(CurriculumSource).where(CurriculumSource.id == curriculum_id)
        return self._db.scalars(stmt).first()

    def update_status(
        self,
        curriculum_id: uuid.UUID,
        status: CurriculumProcessingStatus,
    ) -> CurriculumSource | None:
        """Update the processing status of a curriculum source."""
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
    ) -> CurriculumSource | None:
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
        lesson_id: uuid.UUID,
        original_filename: str,
        file_type: str,
        storage_path: str,
    ) -> CurriculumSource:
        """Create and return a new curriculum source record."""
        record = CurriculumSource(
            lesson_id=lesson_id,
            original_filename=original_filename,
            file_type=file_type,
            storage_path=storage_path,
            processing_status=CurriculumProcessingStatus.pending,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record
