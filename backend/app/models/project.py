import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.user import User


class AssetType(str, enum.Enum):
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


class Project(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "projects"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    title: Mapped[str] = mapped_column(String(500))

    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")  # noqa: F821
    creator: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821
    assets: Mapped[list["ProjectAsset"]] = relationship(
        "ProjectAsset", back_populates="project", lazy="selectin", cascade="all, delete-orphan",
    )


class ProjectAsset(UUIDMixin, Base):
    __tablename__ = "project_assets"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True,
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type", native_enum=False, length=10),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    project: Mapped["Project"] = relationship("Project", back_populates="assets")
