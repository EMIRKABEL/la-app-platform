"""Lesson model."""

from __future__ import annotations

from app.models.enums import LessonStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Lesson(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A lesson within a unit, with lifecycle status."""

    __tablename__ = "lessons"

    unit_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("units.id", ondelete="CASCADE"),
        nullable=False,
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus, name="lesson_status"),
        default=LessonStatus.draft,
        nullable=False,
    )

    unit: Mapped["Unit"] = relationship(back_populates="lessons")
    curriculum_sources: Mapped[list["CurriculumSource"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )
    objectives: Mapped[list["LessonObjective"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Activity.sequence_order",
    )
    versions: Mapped[list["LessonVersion"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="LessonVersion.version_number",
    )

    def __repr__(self) -> str:
        return f"<Lesson {self.number}: {self.title} [{self.status.value}]>"
