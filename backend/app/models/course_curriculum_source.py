"""CourseCurriculumSource model — uploaded curriculum files at course level."""

from __future__ import annotations

from datetime import datetime

from app.models.enums import CurriculumProcessingStatus
from app.models.mixins import UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseCurriculumSource(UUIDPrimaryKeyMixin, Base):
    """An uploaded curriculum source file linked to a course (not a lesson)."""

    __tablename__ = "course_curriculum_sources"

    course_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    processing_status: Mapped[CurriculumProcessingStatus] = mapped_column(
        Enum(CurriculumProcessingStatus, name="curriculum_processing_status"),
        default=CurriculumProcessingStatus.pending,
        nullable=False,
    )
    extracted_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    extracted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    course: Mapped["Course"] = relationship(back_populates="course_curriculum_sources")

    def __repr__(self) -> str:
        return f"<CourseCurriculumSource {self.original_filename} [{self.processing_status.value}]>"
