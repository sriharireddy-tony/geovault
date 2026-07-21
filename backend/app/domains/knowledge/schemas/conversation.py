"""Conversation / message schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    space_id: uuid.UUID
    title: str | None = "New conversation"
    source_ids: list[uuid.UUID] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    space_id: uuid.UUID | None
    created_by: uuid.UUID
    title: str
    scope_type: str
    created_at: datetime


class CitationResponse(BaseModel):
    source_id: uuid.UUID
    source_name: str | None = None
    chunk_id: uuid.UUID | None = None
    page_number: int | None = None
    timestamp_start: float | None = None
    timestamp_end: float | None = None
    snippet: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    model: str | None
    created_at: datetime
    citations: list[CitationResponse] = Field(default_factory=list)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    source_ids: list[uuid.UUID] | None = None
