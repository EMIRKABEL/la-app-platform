"""Pydantic schemas for the Lesson API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LessonBase(BaseModel):
    """Shared base for lesson schemas."""

    number: int
    title: str


class LessonCreate(LessonBase):
    """Schema for creating a lesson."""

    pass


class LessonResponse(LessonBase):
    """Schema for lesson API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    unit_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
