"""Activity model."""

from __future__ import annotations

from app.models.enums import ActivityStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.types import JSONBType


class Activity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An activity within a lesson, with JSON configuration."""

    __tablename__ = "activities"

    lesson_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus, name="activity_status"),
        default=ActivityStatus.draft,
        nullable=False,
    )
    configuration_json: Mapped[dict | None] = mapped_column(
        JSONBType(),
        nullable=True,
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="activities")

    def __repr__(self) -> str:
        return f"<Activity {self.sequence_order}: {self.title} [{self.status.value}]>"
