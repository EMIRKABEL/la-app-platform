"""API package — re-exports all routers."""

from app.api.courses import router as courses_router

__all__ = ["courses_router"]
