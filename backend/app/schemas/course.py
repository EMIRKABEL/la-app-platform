"""Pydantic schemas for the Course API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    """Shared base for course schemas."""

    name: str
    description: str | None = None


class CourseCreate(CourseBase):
    """Schema for creating a course."""

    pass


class CourseUpdate(CourseBase):
    """Schema for updating a course."""

    pass


class CourseResponse(CourseBase):
    """Schema for course API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
