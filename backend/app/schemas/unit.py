"""Pydantic schemas for the Unit API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    """Shared base for unit schemas."""

    number: int
    title: str


class UnitCreate(UnitBase):
    """Schema for creating a unit."""

    pass


class UnitUpdate(UnitBase):
    """Schema for updating a unit."""

    pass


class UnitResponse(UnitBase):
    """Schema for unit API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
