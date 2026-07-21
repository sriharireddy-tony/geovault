"""Search request/response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    space_id: uuid.UUID
    query: str = Field(min_length=1)
    source_ids: list[uuid.UUID] | None = None
    top_k: int = Field(default=8, ge=1, le=50)


class SearchHit(BaseModel):
    chunk_id: str
    source_id: str
    source_name: str | None = None
    content: str
    page_number: int | None = None
    score: float | None = None
