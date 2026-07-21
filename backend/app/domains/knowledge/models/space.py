"""Knowledge space models."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.knowledge.models.enums import SpaceMemberRole
from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class KnowledgeSpace(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "knowledge_spaces"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    members: Mapped[list[KnowledgeSpaceMember]] = relationship(
        back_populates="space", cascade="all, delete-orphan"
    )
    sources: Mapped[list["KnowledgeSource"]] = relationship(
        back_populates="space", cascade="all, delete-orphan"
    )


class KnowledgeSpaceMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_space_members"
    __table_args__ = (UniqueConstraint("space_id", "user_id", name="uq_space_member"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    space_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_spaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=SpaceMemberRole.VIEWER.value, server_default="VIEWER")

    space: Mapped[KnowledgeSpace] = relationship(back_populates="members")
