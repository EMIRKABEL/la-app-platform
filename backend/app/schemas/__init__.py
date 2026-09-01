# LA App Backend

"""Schemas package — re-exports all Pydantic schemas."""

from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate

__all__ = ["CourseCreate", "CourseResponse", "CourseUpdate"]
