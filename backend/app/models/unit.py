"""Unit model."""

from __future__ import annotations

from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Unit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A unit within a course."""

    __tablename__ = "units"

    course_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    course: Mapped["Course"] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="Lesson.number",
    )

    def __repr__(self) -> str:
        return f"<Unit {self.number}: {self.title}>"
