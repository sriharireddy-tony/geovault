import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CreatorInfo


class ImageCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    prompt: str | None = Field(default=None, max_length=50_000)
    project_id: uuid.UUID | None = None


class ImageUpdate(BaseModel):
    project_ids: list[uuid.UUID] = Field(default_factory=list)


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_by: CreatorInfo
    title: str
    prompt: str | None
    file_url: str | None
    project_id: uuid.UUID | None
    project_ids: list[uuid.UUID] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
