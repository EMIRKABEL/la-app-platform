"""End-to-end test: course → unit → lesson → curriculum upload.

This test exercises the full workflow a user would perform:
1. Create a Course
2. Create a Unit inside the Course
3. Create a Lesson inside the Unit
4. Upload a dummy PPTX curriculum file
5. Confirm the file is stored on disk
6. Confirm a CurriculumSource record is created
7. Confirm the file appears in the curriculum listing
"""

import io
import os
import tempfile
import shutil


def test_e2e_curriculum_upload(client, monkeypatch):
    """Full end-to-end curriculum upload workflow."""
    # Use a temp directory for storage
    tmp_storage = tempfile.mkdtemp()
    monkeypatch.setenv("STORAGE_ROOT", tmp_storage)

    # Clear cached settings so the new STORAGE_ROOT takes effect
    from app.core import config
    config.get_settings.cache_clear()

    try:
        # 1. Create Course
        r = client.post(
            "/api/courses",
            json={"name": "E2E Course", "description": "End-to-end test"},
        )
        assert r.status_code == 201
        course_id = r.json()["id"]

        # 2. Create Unit 1
        r2 = client.post(
            f"/api/courses/{course_id}/units",
            json={"number": 1, "title": "Unit 1"},
        )
        assert r2.status_code == 201
        unit_id = r2.json()["id"]

        # 3. Create Lesson 1
        r3 = client.post(
            f"/api/units/{unit_id}/lessons",
            json={"number": 1, "title": "Lesson 1"},
        )
        assert r3.status_code == 201
        assert r3.json()["status"] == "draft"
        lesson_id = r3.json()["id"]

        # 4. Upload a dummy PPTX
        pptx_content = b"fake pptx content for e2e test"
        r4 = client.post(
            f"/api/lessons/{lesson_id}/curriculum",
            files={
                "file": (
                    "e2e-test.pptx",
                    io.BytesIO(pptx_content),
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            },
        )
        assert r4.status_code == 201
        body = r4.json()
        assert body["original_filename"] == "e2e-test.pptx"
        assert body["file_type"] == "pptx"
        assert body["processing_status"] == "pending"
        assert body["lesson_id"] == lesson_id

        # 5. Confirm the file is stored on disk
        storage_path = body["storage_path"]
        full_path = os.path.join(tmp_storage, storage_path.replace("/", os.sep))
        assert os.path.isfile(full_path), f"File not found at {full_path}"

        # Verify file content
        with open(full_path, "rb") as f:
            assert f.read() == pptx_content

        # 6. Confirm CurriculumSource record exists in DB
        # (already validated via the 201 response above)

        # 7. Confirm the file appears in the curriculum listing
        r5 = client.get(f"/api/lessons/{lesson_id}/curriculum")
        assert r5.status_code == 200
        sources = r5.json()
        assert len(sources) == 1
        assert sources[0]["original_filename"] == "e2e-test.pptx"
        assert sources[0]["file_type"] == "pptx"
        assert sources[0]["processing_status"] == "pending"

    finally:
        config.get_settings.cache_clear()
        shutil.rmtree(tmp_storage, ignore_errors=True)
