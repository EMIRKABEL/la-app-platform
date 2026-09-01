"""Tests for Course API endpoints."""

import uuid


def test_create_course(client):
    """POST /api/courses should create and return a course."""
    payload = {"name": "English A1", "description": "Beginner English course"}
    response = client.post("/api/courses", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "English A1"
    assert body["description"] == "Beginner English course"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_course_minimal(client):
    """POST /api/courses should work with name only (description optional)."""
    payload = {"name": "Math Basics"}
    response = client.post("/api/courses", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Math Basics"
    assert body["description"] is None


def test_list_courses(client):
    """GET /api/courses should return all courses."""
    # Create two courses
    client.post("/api/courses", json={"name": "Course A", "description": "First"})
    client.post("/api/courses", json={"name": "Course B", "description": "Second"})

    response = client.get("/api/courses")

    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 2
    # Both courses should be present
    names = [c["name"] for c in courses]
    assert "Course B" in names
    assert "Course A" in names


def test_get_course_by_id(client):
    """GET /api/courses/{id} should return the correct course."""
    create_resp = client.post(
        "/api/courses",
        json={"name": "Physics 101", "description": "Intro physics"},
    )
    course_id = create_resp.json()["id"]

    response = client.get(f"/api/courses/{course_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Physics 101"
    assert body["description"] == "Intro physics"
    assert body["id"] == course_id


def test_get_course_404(client):
    """GET /api/courses/{random-uuid} should return 404."""
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/courses/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"
