"""Tests for the /health endpoint and app startup."""

from fastapi.testclient import TestClient

from app.main import app


def test_app_starts_successfully():
    """The FastAPI application should instantiate without errors."""
    assert app is not None
    assert app.title == "LA App Backend"


def test_health_returns_200(client):
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client):
    """GET /health should return status 'ok' and the correct service name."""
    response = client.get("/health")
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "la-app-backend"
