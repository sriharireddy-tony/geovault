"""Knowledge space request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeSpaceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class KnowledgeSpaceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class KnowledgeSpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_by: uuid.UUID
    title: str
    description: str | None
    is_active: bool
    created_at: datetime
    member_role: str | None = None
    source_count: int = 0
