import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CreatorInfo


class AudioCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    prompt: str | None = Field(default=None, max_length=2500)
    language: str = Field(default="en-IN", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    speaker: str = Field(default="shubh", max_length=30)
    project_id: uuid.UUID | None = None


class AudioUpdate(BaseModel):
    project_ids: list[uuid.UUID] = Field(default_factory=list)


class AudioResponse(BaseModel):
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
