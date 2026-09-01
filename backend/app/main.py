"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    courses_router,
    curriculum_router,
    lessons_router,
    units_router,
)
from app.core import settings

app = FastAPI(
    title="LA App Backend",
    description="Content Factory backend API for the LA App platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

# CORS — allow the Content Factory frontend during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """Return service health status."""
    return {
        "status": "ok",
        "service": "la-app-backend",
    }


app.include_router(courses_router)
app.include_router(units_router)
app.include_router(lessons_router)
app.include_router(curriculum_router)
