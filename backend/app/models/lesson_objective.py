"""LessonObjective model."""

from __future__ import annotations

from datetime import datetime

from app.models.mixins import UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class LessonObjective(UUIDPrimaryKeyMixin, Base):
    """A learning objective associated with a lesson."""

    __tablename__ = "lesson_objectives"

    lesson_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    objective_text: Mapped[str] = mapped_column(String(1024), nullable=False)
    skill: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="objectives")

    def __repr__(self) -> str:
        return f"<LessonObjective {self.objective_text[:50]}>"
