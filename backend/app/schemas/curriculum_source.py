"""Pydantic schemas for the CurriculumSource API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CurriculumSourceResponse(BaseModel):
    """Schema for curriculum source API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    original_filename: str
    file_type: str | None
    storage_path: str
    uploaded_at: datetime
    processing_status: str
