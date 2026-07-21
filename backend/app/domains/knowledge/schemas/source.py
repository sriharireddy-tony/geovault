"""Knowledge source request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceCreateText(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    content: str = Field(min_length=1)
    type: str = "TEXT"


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    space_id: uuid.UUID
    created_by: uuid.UUID
    type: str
    name: str
    status: str
    storage_key: str | None
    mime_type: str | None
    byte_size: int | None
    error_message: str | None
    created_at: datetime
