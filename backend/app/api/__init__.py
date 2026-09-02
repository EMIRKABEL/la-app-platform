"""API package — re-exports all routers."""

from app.api.course_curriculum import router as course_curriculum_router
from app.api.courses import router as courses_router
from app.api.curriculum import router as curriculum_router
from app.api.lessons import router as lessons_router
from app.api.units import router as units_router

__all__ = [
    "course_curriculum_router",
    "courses_router",
    "curriculum_router",
    "lessons_router",
    "units_router",
]
