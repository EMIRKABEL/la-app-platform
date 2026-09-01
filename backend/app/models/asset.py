"""Asset model — media assets with approval workflow."""

from __future__ import annotations

from app.models.enums import AssetApprovalStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.session import Base

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.types import JSONBType


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A media asset with metadata and approval status."""

    __tablename__ = "assets"

    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONBType(),
        nullable=True,
    )
    approval_status: Mapped[AssetApprovalStatus] = mapped_column(
        Enum(AssetApprovalStatus, name="asset_approval_status"),
        default=AssetApprovalStatus.pending,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Asset {self.name} [{self.asset_type}] [{self.approval_status.value}]>"
