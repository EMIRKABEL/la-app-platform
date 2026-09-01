"""LessonVersion model — versioned snapshots of lesson content."""

from __future__ import annotations

from datetime import datetime

from app.models.enums import LessonVersionStatus
from app.models.mixins import UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.types import JSONBType


class LessonVersion(UUIDPrimaryKeyMixin, Base):
    """A versioned snapshot of a lesson's content as JSONB."""

    __tablename__ = "lesson_versions"

    lesson_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_json: Mapped[dict | None] = mapped_column(
        JSONBType(),
        nullable=True,
    )
    status: Mapped[LessonVersionStatus] = mapped_column(
        Enum(LessonVersionStatus, name="lesson_version_status"),
        default=LessonVersionStatus.draft,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<LessonVersion v{self.version_number} [{self.status.value}]>"
