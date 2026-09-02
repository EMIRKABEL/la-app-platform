"""Pydantic schemas for course-level curriculum source API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CourseCurriculumSourceResponse(BaseModel):
    """Schema for course curriculum source API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    original_filename: str
    file_type: str | None
    storage_path: str
    uploaded_at: datetime
    processing_status: str
    extracted_at: datetime | None = None


class CourseExtractionResponse(BaseModel):
    """Schema for course curriculum extraction responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    original_filename: str
    file_type: str | None
    processing_status: str
    extracted_at: datetime | None
    extracted_data: dict[str, Any] | None
