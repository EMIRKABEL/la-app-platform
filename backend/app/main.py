"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core import settings

app = FastAPI(
    title="LA App Backend",
    description="Content Factory backend API for the LA App platform",
    version="0.1.0",
    debug=settings.DEBUG,
)


@app.get("/health")
def health_check() -> dict:
    """Return service health status."""
    return {
        "status": "ok",
        "service": "la-app-backend",
    }
