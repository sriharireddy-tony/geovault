"""Knowledge source + extracted content models."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.knowledge.models.enums import SourceStatus
from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class KnowledgeSource(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "knowledge_sources"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    space_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=SourceStatus.CREATED.value, server_default="CREATED", index=True
    )
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_version: Mapped[str] = mapped_column(String(32), default="v1", server_default="v1")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    space: Mapped["KnowledgeSpace"] = relationship(back_populates="sources")
    content_blocks: Mapped[list[ContentBlock]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class ContentBlock(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "content_blocks"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), default="TEXT", server_default="TEXT")
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp_end: Mapped[float | None] = mapped_column(Float, nullable=True)
    section: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ordinal: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    source: Mapped[KnowledgeSource] = relationship(back_populates="content_blocks")


class DocumentChunk(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "document_chunks"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    space_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    block_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("content_blocks.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp_end: Mapped[float | None] = mapped_column(Float, nullable=True)
    section: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    source: Mapped[KnowledgeSource] = relationship(back_populates="chunks")
