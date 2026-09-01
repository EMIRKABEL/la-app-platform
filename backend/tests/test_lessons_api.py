"""Tests for Lesson API endpoints."""

import uuid


def _create_course_unit(client):
    """Helper: create a course with a unit and return (course_id, unit_id)."""
    course_resp = client.post(
        "/api/courses",
        json={"name": "Test Course", "description": "For lesson tests"},
    )
    course_id = course_resp.json()["id"]
    unit_resp = client.post(
        f"/api/courses/{course_id}/units",
        json={"number": 1, "title": "Unit 1"},
    )
    return course_id, unit_resp.json()["id"]


def test_create_lesson(client):
    """POST /api/units/{unit_id}/lessons should create a lesson with draft status."""
    _, unit_id = _create_course_unit(client)
    payload = {"number": 1, "title": "Greetings"}
    response = client.post(f"/api/units/{unit_id}/lessons", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["number"] == 1
    assert body["title"] == "Greetings"
    assert body["unit_id"] == unit_id
    assert body["status"] == "draft"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_list_lessons(client):
    """GET /api/units/{unit_id}/lessons should return all lessons ordered by number."""
    _, unit_id = _create_course_unit(client)
    client.post(
        f"/api/units/{unit_id}/lessons",
        json={"number": 2, "title": "Second Lesson"},
    )
    client.post(
        f"/api/units/{unit_id}/lessons",
        json={"number": 1, "title": "First Lesson"},
    )

    response = client.get(f"/api/units/{unit_id}/lessons")

    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) == 2
    assert lessons[0]["number"] == 1
    assert lessons[0]["title"] == "First Lesson"
    assert lessons[1]["number"] == 2
    assert lessons[1]["title"] == "Second Lesson"


def test_get_lesson(client):
    """GET /api/lessons/{lesson_id} should return the correct lesson."""
    _, unit_id = _create_course_unit(client)
    create_resp = client.post(
        f"/api/units/{unit_id}/lessons",
        json={"number": 1, "title": "Get Me"},
    )
    lesson_id = create_resp.json()["id"]

    response = client.get(f"/api/lessons/{lesson_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["number"] == 1
    assert body["title"] == "Get Me"
    assert body["id"] == lesson_id
    assert body["unit_id"] == unit_id
    assert body["status"] == "draft"


def test_get_lesson_404(client):
    """GET /api/lessons/{random-uuid} should return 404."""
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/lessons/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Lesson not found"
