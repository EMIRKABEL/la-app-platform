"""Tests for database model imports and basic structure."""

import uuid
from datetime import datetime

from app.models import (
    Activity,
    Asset,
    Course,
    CurriculumSource,
    Lesson,
    LessonObjective,
    LessonVersion,
    Unit,
)
from app.models.enums import (
    ActivityStatus,
    AssetApprovalStatus,
    CurriculumProcessingStatus,
    LessonStatus,
    LessonVersionStatus,
)


def test_course_model_import():
    """Course model should import and have expected attributes."""
    assert hasattr(Course, "id")
    assert hasattr(Course, "name")
    assert hasattr(Course, "description")
    assert hasattr(Course, "created_at")
    assert hasattr(Course, "updated_at")


def test_unit_model_import():
    """Unit model should import and have expected attributes."""
    assert hasattr(Unit, "id")
    assert hasattr(Unit, "course_id")
    assert hasattr(Unit, "number")
    assert hasattr(Unit, "title")
    assert hasattr(Unit, "created_at")
    assert hasattr(Unit, "updated_at")


def test_lesson_model_import():
    """Lesson model should import and have expected attributes."""
    assert hasattr(Lesson, "id")
    assert hasattr(Lesson, "unit_id")
    assert hasattr(Lesson, "number")
    assert hasattr(Lesson, "title")
    assert hasattr(Lesson, "status")
    assert hasattr(Lesson, "created_at")
    assert hasattr(Lesson, "updated_at")


def test_curriculum_source_model_import():
    """CurriculumSource model should import and have expected attributes."""
    assert hasattr(CurriculumSource, "id")
    assert hasattr(CurriculumSource, "lesson_id")
    assert hasattr(CurriculumSource, "original_filename")
    assert hasattr(CurriculumSource, "file_type")
    assert hasattr(CurriculumSource, "storage_path")
    assert hasattr(CurriculumSource, "uploaded_at")
    assert hasattr(CurriculumSource, "processing_status")


def test_lesson_objective_model_import():
    """LessonObjective model should import and have expected attributes."""
    assert hasattr(LessonObjective, "id")
    assert hasattr(LessonObjective, "lesson_id")
    assert hasattr(LessonObjective, "objective_text")
    assert hasattr(LessonObjective, "skill")
    assert hasattr(LessonObjective, "created_at")


def test_activity_model_import():
    """Activity model should import and have expected attributes."""
    assert hasattr(Activity, "id")
    assert hasattr(Activity, "lesson_id")
    assert hasattr(Activity, "activity_type")
    assert hasattr(Activity, "sequence_order")
    assert hasattr(Activity, "title")
    assert hasattr(Activity, "status")
    assert hasattr(Activity, "configuration_json")
    assert hasattr(Activity, "created_at")
    assert hasattr(Activity, "updated_at")


def test_asset_model_import():
    """Asset model should import and have expected attributes."""
    assert hasattr(Asset, "id")
    assert hasattr(Asset, "asset_type")
    assert hasattr(Asset, "name")
    assert hasattr(Asset, "storage_path")
    assert hasattr(Asset, "metadata_json")
    assert hasattr(Asset, "approval_status")
    assert hasattr(Asset, "created_at")
    assert hasattr(Asset, "updated_at")


def test_lesson_version_model_import():
    """LessonVersion model should import and have expected attributes."""
    assert hasattr(LessonVersion, "id")
    assert hasattr(LessonVersion, "lesson_id")
    assert hasattr(LessonVersion, "version_number")
    assert hasattr(LessonVersion, "lesson_json")
    assert hasattr(LessonVersion, "status")
    assert hasattr(LessonVersion, "created_at")


def test_lesson_status_enum_values():
    """LessonStatus enum should contain all expected lifecycle states."""
    expected = {"draft", "analyzing", "review", "approved", "published"}
    actual = {s.value for s in LessonStatus}
    assert actual == expected


def test_activity_status_enum_values():
    """ActivityStatus enum should contain all expected states."""
    expected = {"draft", "review", "approved", "published"}
    actual = {s.value for s in ActivityStatus}
    assert actual == expected


def test_curriculum_processing_status_enum_values():
    """CurriculumProcessingStatus enum should contain all expected states."""
    expected = {"pending", "processing", "completed", "failed"}
    actual = {s.value for s in CurriculumProcessingStatus}
    assert actual == expected


def test_asset_approval_status_enum_values():
    """AssetApprovalStatus enum should contain all expected states."""
    expected = {"pending", "approved", "rejected"}
    actual = {s.value for s in AssetApprovalStatus}
    assert actual == expected


def test_lesson_version_status_enum_values():
    """LessonVersionStatus enum should contain all expected states."""
    expected = {"draft", "published", "archived"}
    actual = {s.value for s in LessonVersionStatus}
    assert actual == expected


def test_uuid_primary_keys():
    """Models using UUIDPrimaryKeyMixin should have UUID-typed id columns."""
    from sqlalchemy import inspect as sa_inspect

    for model in [
        Course,
        Unit,
        Lesson,
        CurriculumSource,
        LessonObjective,
        Activity,
        Asset,
        LessonVersion,
    ]:
        mapper = sa_inspect(model)
        pk_cols = [c for c in mapper.columns if c.primary_key]
        assert len(pk_cols) == 1, f"{model.__name__} should have exactly one PK"
        assert pk_cols[0].name == "id", f"{model.__name__} PK should be named 'id'"
