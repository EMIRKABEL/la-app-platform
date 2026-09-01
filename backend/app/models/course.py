"""Course model."""

from __future__ import annotations

from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Course(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level container for a course."""

    __tablename__ = "courses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    units: Mapped[list["Unit"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Unit.number",
    )

    def __repr__(self) -> str:
        return f"<Course {self.name}>"
