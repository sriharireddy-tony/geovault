import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.project import Project


class Audio(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "audios"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    title: Mapped[str] = mapped_column(String(500))
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")  # noqa: F821
    creator: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821
    project: Mapped["Project"] = relationship("Project", lazy="selectin")  # noqa: F821
