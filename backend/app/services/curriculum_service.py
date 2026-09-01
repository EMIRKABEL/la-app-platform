"""Service layer for curriculum upload and listing."""

from __future__ import annotations

import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.curriculum_source import CurriculumSource
from app.repositories.curriculum_source_repository import (
    CurriculumSourceRepository,
)
from app.repositories.lesson_repository import LessonRepository
from app.services.storage import LocalStorageProvider, StorageProvider

# Supported file extensions for curriculum uploads
ALLOWED_EXTENSIONS = {".pptx", ".pdf", ".docx", ".xlsx"}

# 50 MB max upload for development
MAX_FILE_SIZE = 50 * 1024 * 1024


class CurriculumService:
    """Business logic for curriculum source files."""

    def __init__(
        self,
        db: Session,
        storage: StorageProvider | None = None,
    ) -> None:
        self._db = db
        self._repo = CurriculumSourceRepository(db)
        self._lesson_repo = LessonRepository(db)
        self._storage = storage or self._default_storage()

    @staticmethod
    def _default_storage() -> StorageProvider:
        """Create the default local storage provider from settings."""
        from app.core.config import get_settings

        s = get_settings()
        root = s.STORAGE_ROOT
        # Resolve relative paths from the backend/ directory
        if not os.path.isabs(root):
            backend_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            root = os.path.join(backend_dir, root)
        return LocalStorageProvider(root)

    def list_curriculum(
        self, lesson_id: uuid.UUID
    ) -> list[CurriculumSource]:
        """Return all curriculum sources for a lesson."""
        return self._repo.list_by_lesson(lesson_id)

    def upload_curriculum(
        self,
        lesson_id: uuid.UUID,
        file: UploadFile,
    ) -> CurriculumSource:
        """Validate, store, and record a curriculum file upload.

        Raises ``ValueError`` for unsupported file types.
        Raises ``FileNotFoundError`` if the lesson does not exist.
        """
        # Verify the lesson exists
        lesson = self._lesson_repo.get_lesson(lesson_id)
        if lesson is None:
            raise FileNotFoundError("Lesson not found")

        # Validate file extension
        original_filename = file.filename or "unnamed"
        _, ext = os.path.splitext(original_filename)
        ext_lower = ext.lower()

        if ext_lower not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {ext_lower}. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # Read file data (with size guard)
        data = file.file.read(MAX_FILE_SIZE + 1)
        if len(data) > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large. Maximum size is "
                f"{MAX_FILE_SIZE // (1024 * 1024)} MB."
            )

        # Get the full hierarchy for the storage path — we need
        # course_id and unit_id from the lesson's unit
        from app.repositories.unit_repository import UnitRepository

        unit_repo = UnitRepository(self._db)
        unit = unit_repo.get_unit(lesson.unit_id)
        if unit is None:
            raise FileNotFoundError("Unit not found for lesson")

        # Save the file via the storage provider
        storage_path = self._storage.save_file(
            course_id=str(unit.course_id),
            unit_id=str(unit.id),
            lesson_id=str(lesson.id),
            original_filename=original_filename,
            data=data,
        )

        # Create the database record
        file_type = ext_lower.lstrip(".")
        record = self._repo.create(
            lesson_id=lesson_id,
            original_filename=original_filename,
            file_type=file_type,
            storage_path=storage_path,
        )
        return record
