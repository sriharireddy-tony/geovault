"""Ingestion job tracking model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.knowledge.models.enums import SourceStatus
from app.models.base import Base, TimestampMixin, UUIDMixin


class IngestionJob(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ingestion_jobs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False, index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), default=SourceStatus.PROCESSING.value, server_default="PROCESSING"
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
