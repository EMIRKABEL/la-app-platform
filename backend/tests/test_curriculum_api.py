"""Tests for curriculum upload and listing endpoints."""

import io
import os
import uuid
import tempfile
import shutil


def _create_course_unit_lesson(client):
    """Helper: create course → unit → lesson and return lesson_id."""
    course_resp = client.post(
        "/api/courses",
        json={"name": "Curriculum Test Course", "description": "For upload tests"},
    )
    course_id = course_resp.json()["id"]
    unit_resp = client.post(
        f"/api/courses/{course_id}/units",
        json={"number": 1, "title": "Unit 1"},
    )
    unit_id = unit_resp.json()["id"]
    lesson_resp = client.post(
        f"/api/units/{unit_id}/lessons",
        json={"number": 1, "title": "Lesson 1"},
    )
    return lesson_resp.json()["id"]


def _make_dummy_file(filename: str, content: bytes = b"dummy content"):
    """Return a BytesIO wrapped in a dict suitable for the files= parameter."""
    return {"file": (filename, io.BytesIO(content), "application/octet-stream")}


def test_upload_pptx(client):
    """POST /api/lessons/{lesson_id}/curriculum with .pptx should succeed."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("lesson-slides.pptx", b"fake pptx data")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["lesson_id"] == lesson_id
    assert body["original_filename"] == "lesson-slides.pptx"
    assert body["file_type"] == "pptx"
    assert body["storage_path"].startswith("curriculum/")
    assert body["processing_status"] == "pending"
    assert "id" in body
    assert "uploaded_at" in body


def test_upload_pdf(client):
    """POST /api/lessons/{lesson_id}/curriculum with .pdf should succeed."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("curriculum.pdf", b"%PDF-1.4 fake")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "curriculum.pdf"
    assert body["file_type"] == "pdf"
    assert body["processing_status"] == "pending"


def test_upload_docx(client):
    """POST /api/lessons/{lesson_id}/curriculum with .docx should succeed."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("notes.docx", b"fake docx")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "docx"


def test_upload_xlsx(client):
    """POST /api/lessons/{lesson_id}/curriculum with .xlsx should succeed."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("vocab.xlsx", b"fake xlsx")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "xlsx"


def test_reject_unsupported_file_type(client):
    """POST curriculum with .txt should be rejected with 415."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("notes.txt", b"plain text")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 415
    detail = response.json()["detail"]
    assert ".txt" in detail
    assert "pptx" in detail
    assert "pdf" in detail
    assert "docx" in detail
    assert "xlsx" in detail


def test_curriculum_database_record(client):
    """Upload should create a CurriculumSource record in the database."""
    lesson_id = _create_course_unit_lesson(client)
    files = _make_dummy_file("tracked.pptx", b"tracked content")

    response = client.post(f"/api/lessons/{lesson_id}/curriculum", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "tracked.pptx"
    assert body["file_type"] == "pptx"
    assert body["storage_path"] != ""
    assert body["processing_status"] == "pending"
    assert body["lesson_id"] == lesson_id


def test_list_curriculum_sources(client):
    """GET /api/lessons/{lesson_id}/curriculum should list uploaded files."""
    lesson_id = _create_course_unit_lesson(client)

    # Upload two files
    client.post(
        f"/api/lessons/{lesson_id}/curriculum",
        files=_make_dummy_file("first.pptx", b"one"),
    )
    client.post(
        f"/api/lessons/{lesson_id}/curriculum",
        files=_make_dummy_file("second.pdf", b"two"),
    )

    response = client.get(f"/api/lessons/{lesson_id}/curriculum")

    assert response.status_code == 200
    sources = response.json()
    assert len(sources) == 2
    filenames = [s["original_filename"] for s in sources]
    assert "first.pptx" in filenames
    assert "second.pdf" in filenames
    # All should be pending
    for s in sources:
        assert s["processing_status"] == "pending"


def test_list_curriculum_empty(client):
    """GET /api/lessons/{lesson_id}/curriculum on a lesson with no uploads returns []."""
    lesson_id = _create_course_unit_lesson(client)
    response = client.get(f"/api/lessons/{lesson_id}/curriculum")

    assert response.status_code == 200
    assert response.json() == []


def test_upload_curriculum_missing_lesson_404(client):
    """POST curriculum to a non-existent lesson should return 404."""
    random_id = str(uuid.uuid4())
    files = _make_dummy_file("orphan.pdf", b"no lesson")

    response = client.post(f"/api/lessons/{random_id}/curriculum", files=files)

    assert response.status_code == 404
    assert response.json()["detail"] == "Lesson not found"


def test_safe_filename_no_path_traversal():
    """``sanitize_filename`` must strip path components and unsafe chars."""
    from app.services.storage import sanitize_filename

    # Path traversal attempt — only the basename should survive
    safe = sanitize_filename("../../../etc/passwd.pptx")
    assert safe == "passwd.pptx"
    assert ".." not in safe
    assert "/" not in safe
    assert "\\" not in safe

    # Null bytes and spaces are replaced
    safe2 = sanitize_filename("bad\x00name.pdf")
    assert "\x00" not in safe2

    # Leading dots are stripped
    safe3 = sanitize_filename(".hidden.docx")
    assert not safe3.startswith(".")

    # Empty fallback
    safe4 = sanitize_filename("")
    assert len(safe4) > 0


def test_storage_path_within_root():
    """``LocalStorageProvider`` must store files inside the storage root."""
    from app.services.storage import LocalStorageProvider

    tmp = tempfile.mkdtemp()
    try:
        provider = LocalStorageProvider(tmp)
        storage_path = provider.save_file(
            course_id="cid",
            unit_id="uid",
            lesson_id="lid",
            original_filename="../../../sneaky.pptx",
            data=b"safe data",
        )
        assert ".." not in storage_path
        assert storage_path.startswith("curriculum/")
        assert provider.file_exists(storage_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
