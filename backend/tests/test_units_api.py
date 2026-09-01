"""Tests for Unit API endpoints."""

import uuid


def _create_course(client):
    """Helper: create a course and return its id."""
    resp = client.post(
        "/api/courses",
        json={"name": "Test Course", "description": "For unit tests"},
    )
    return resp.json()["id"]


def test_create_unit(client):
    """POST /api/courses/{course_id}/units should create and return a unit."""
    course_id = _create_course(client)
    payload = {"number": 1, "title": "Introduction"}
    response = client.post(f"/api/courses/{course_id}/units", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["number"] == 1
    assert body["title"] == "Introduction"
    assert body["course_id"] == course_id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_list_units(client):
    """GET /api/courses/{course_id}/units should return all units ordered by number."""
    course_id = _create_course(client)
    client.post(
        f"/api/courses/{course_id}/units",
        json={"number": 2, "title": "Second Unit"},
    )
    client.post(
        f"/api/courses/{course_id}/units",
        json={"number": 1, "title": "First Unit"},
    )

    response = client.get(f"/api/courses/{course_id}/units")

    assert response.status_code == 200
    units = response.json()
    assert len(units) == 2
    # Ordered by number
    assert units[0]["number"] == 1
    assert units[0]["title"] == "First Unit"
    assert units[1]["number"] == 2
    assert units[1]["title"] == "Second Unit"


def test_get_unit(client):
    """GET /api/units/{unit_id} should return the correct unit."""
    course_id = _create_course(client)
    create_resp = client.post(
        f"/api/courses/{course_id}/units",
        json={"number": 1, "title": "Get Me"},
    )
    unit_id = create_resp.json()["id"]

    response = client.get(f"/api/units/{unit_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["number"] == 1
    assert body["title"] == "Get Me"
    assert body["id"] == unit_id
    assert body["course_id"] == course_id


def test_get_unit_404(client):
    """GET /api/units/{random-uuid} should return 404."""
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/units/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Unit not found"


def test_list_units_empty(client):
    """GET /api/courses/{course_id}/units on a new course should return []."""
    course_id = _create_course(client)
    response = client.get(f"/api/courses/{course_id}/units")

    assert response.status_code == 200
    assert response.json() == []
