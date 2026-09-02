"""Service layer for course-level curriculum upload, listing, and extraction."""

from __future__ import annotations

import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.course_curriculum_source import CourseCurriculumSource
from app.models.enums import CurriculumProcessingStatus
from app.repositories.course_curriculum_source_repository import (
    CourseCurriculumSourceRepository,
)
from app.repositories.course_repository import CourseRepository
from app.services.extractors import PptxExtractor
from app.services.extractors.base import BaseExtractor
from app.services.storage import LocalStorageProvider, StorageProvider

# Reuse the same constants as the lesson-level service
from app.services.curriculum_service import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Registry of extractors keyed by file extension
_EXTRACTORS: dict[str, BaseExtractor] = {
    ".pptx": PptxExtractor(),
}


class CourseCurriculumService:
    """Business logic for course-level curriculum source files."""

    def __init__(
        self,
        db: Session,
        storage: StorageProvider | None = None,
    ) -> None:
        self._db = db
        self._repo = CourseCurriculumSourceRepository(db)
        self._course_repo = CourseRepository(db)
        self._storage = storage or self._default_storage()

    @staticmethod
    def _default_storage() -> StorageProvider:
        """Create the default local storage provider from settings."""
        from app.core.config import get_settings

        s = get_settings()
        root = s.STORAGE_ROOT
        if not os.path.isabs(root):
            backend_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            root = os.path.join(backend_dir, root)
        return LocalStorageProvider(root)

    def list_curriculum(
        self, course_id: uuid.UUID
    ) -> list[CourseCurriculumSource]:
        """Return all curriculum sources for a course."""
        return self._repo.list_by_course(course_id)

    def upload_curriculum(
        self,
        course_id: uuid.UUID,
        file: UploadFile,
    ) -> CourseCurriculumSource:
        """Validate, store, and record a course-level curriculum file upload.

        Raises ``ValueError`` for unsupported file types.
        Raises ``FileNotFoundError`` if the course does not exist.
        """
        # Verify the course exists
        course = self._course_repo.get_course(course_id)
        if course is None:
            raise FileNotFoundError("Course not found")

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

        # Save the file via the storage provider
        storage_path = self._storage.save_course_file(
            course_id=str(course.id),
            original_filename=original_filename,
            data=data,
        )

        # Create the database record
        file_type = ext_lower.lstrip(".")
        record = self._repo.create(
            course_id=course_id,
            original_filename=original_filename,
            file_type=file_type,
            storage_path=storage_path,
        )
        return record

    def upload_multiple_curriculum(
        self,
        course_id: uuid.UUID,
        files: list[UploadFile],
    ) -> list[CourseCurriculumSource]:
        """Upload multiple curriculum files for a course in one call.

        If any file fails validation, the error is collected and the
        remaining files are still processed.  Returns the successfully
        created records.  Raises ``FileNotFoundError`` if the course
        does not exist.
        """
        # Verify the course exists first
        course = self._course_repo.get_course(course_id)
        if course is None:
            raise FileNotFoundError("Course not found")

        records: list[CourseCurriculumSource] = []
        for f in files:
            try:
                record = self.upload_curriculum(course_id, f)
                records.append(record)
            except ValueError:
                # Skip unsupported files — caller can check
                # len(records) vs len(files) to detect skips
                continue
        return records

    def extract_curriculum(
        self, curriculum_id: uuid.UUID
    ) -> CourseCurriculumSource:
        """Extract structured content from a course curriculum source file.

        Reuses the same extractor registry as lesson-level extraction.

        Raises:
            FileNotFoundError: If the curriculum source does not exist.
            ValueError: If the file type is unsupported for extraction.
        """
        record = self._repo.get_by_id(curriculum_id)
        if record is None:
            raise FileNotFoundError("Course curriculum source not found")

        file_type = (record.file_type or "").lower()
        ext = f".{file_type}" if file_type else ""

        extractor = _EXTRACTORS.get(ext)
        if extractor is None:
            raise ValueError(
                f"Extraction not supported for file type '{ext}'. "
                f"Supported: {', '.join(sorted(_EXTRACTORS.keys()))}"
            )

        # Transition to processing
        self._repo.update_status(
            curriculum_id, CurriculumProcessingStatus.processing
        )

        try:
            # Read the file from storage
            file_bytes = self._storage.read_file(record.storage_path)

            # Extract
            result = extractor.extract(file_bytes)

            # Save extraction and transition to completed
            record = self._repo.save_extraction(
                curriculum_id,
                extracted_data=dict(result),
            )
            return record  # type: ignore[return-value]

        except Exception:
            # Transition to failed on any error
            self._repo.update_status(
                curriculum_id, CurriculumProcessingStatus.failed
            )
            raise

    def get_extraction(
        self, curriculum_id: uuid.UUID
    ) -> CourseCurriculumSource | None:
        """Return the curriculum source with its extracted data."""
        return self._repo.get_by_id(curriculum_id)
