"""Initial schema: courses, units, lessons, curriculum sources, objectives, activities, assets, lesson versions.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-01 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- Enum types --
    lesson_status = sa.Enum(
        "draft", "analyzing", "review", "approved", "published",
        name="lesson_status",
    )
    activity_status = sa.Enum(
        "draft", "review", "approved", "published",
        name="activity_status",
    )
    curriculum_processing_status = sa.Enum(
        "pending", "processing", "completed", "failed",
        name="curriculum_processing_status",
    )
    asset_approval_status = sa.Enum(
        "pending", "approved", "rejected",
        name="asset_approval_status",
    )
    lesson_version_status = sa.Enum(
        "draft", "published", "archived",
        name="lesson_version_status",
    )

    # -- Courses --
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Units --
    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Lessons --
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", lesson_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Curriculum Sources --
    op.create_table(
        "curriculum_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("file_type", sa.String(100), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processing_status", curriculum_processing_status, nullable=False, server_default="pending"),
    )

    # -- Lesson Objectives --
    op.create_table(
        "lesson_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("objective_text", sa.String(1024), nullable=False),
        sa.Column("skill", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Activities --
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", activity_status, nullable=False, server_default="draft"),
        sa.Column("configuration_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Assets --
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("asset_type", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("approval_status", asset_approval_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Lesson Versions --
    op.create_table(
        "lesson_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("lesson_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", lesson_version_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # -- Indexes --
    op.create_index("ix_units_course_id", "units", ["course_id"])
    op.create_index("ix_lessons_unit_id", "lessons", ["unit_id"])
    op.create_index("ix_curriculum_sources_lesson_id", "curriculum_sources", ["lesson_id"])
    op.create_index("ix_lesson_objectives_lesson_id", "lesson_objectives", ["lesson_id"])
    op.create_index("ix_activities_lesson_id", "activities", ["lesson_id"])
    op.create_index("ix_lesson_versions_lesson_id", "lesson_versions", ["lesson_id"])


def downgrade() -> None:
    op.drop_table("lesson_versions")
    op.drop_table("assets")
    op.drop_table("activities")
    op.drop_table("lesson_objectives")
    op.drop_table("curriculum_sources")
    op.drop_table("lessons")
    op.drop_table("units")
    op.drop_table("courses")

    sa.Enum(name="lesson_version_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="asset_approval_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="curriculum_processing_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="activity_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="lesson_status").drop(op.get_bind(), checkfirst=True)
