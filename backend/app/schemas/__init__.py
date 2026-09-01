"""Schemas package — re-exports all Pydantic schemas."""

from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.schemas.curriculum_source import CurriculumSourceResponse
from app.schemas.lesson import LessonCreate, LessonResponse
from app.schemas.unit import UnitCreate, UnitResponse, UnitUpdate

__all__ = [
    "CourseCreate",
    "CourseResponse",
    "CourseUpdate",
    "CurriculumSourceResponse",
    "LessonCreate",
    "LessonResponse",
    "UnitCreate",
    "UnitResponse",
    "UnitUpdate",
]
