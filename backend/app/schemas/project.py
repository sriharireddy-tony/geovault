import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import AssetType
from app.schemas.audio import AudioResponse
from app.schemas.common import CreatorInfo
from app.schemas.image import ImageResponse
from app.schemas.video import VideoResponse


class ProjectAssetCreate(BaseModel):
    asset_type: AssetType
    asset_id: uuid.UUID


class ProjectAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    asset_type: AssetType
    asset_id: uuid.UUID


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    assets: list[ProjectAssetCreate] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    assets: list[ProjectAssetCreate] | None = None


class ProjectSelectionUpdate(BaseModel):
    audio_ids: list[uuid.UUID] = Field(default_factory=list)
    image_ids: list[uuid.UUID] = Field(default_factory=list)
    video_ids: list[uuid.UUID] = Field(default_factory=list)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_by: CreatorInfo
    title: str
    is_active: bool
    created_at: datetime
    assets: list[ProjectAssetResponse] = Field(default_factory=list)


class MediaBucket(BaseModel):
    audios: list[AudioResponse] = Field(default_factory=list)
    images: list[ImageResponse] = Field(default_factory=list)
    videos: list[VideoResponse] = Field(default_factory=list)


class ProjectDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_by: CreatorInfo
    title: str
    is_active: bool
    created_at: datetime
    assets: list[ProjectAssetResponse] = Field(default_factory=list)
    available_media: MediaBucket = Field(default_factory=MediaBucket)
    selected_media: MediaBucket = Field(default_factory=MediaBucket)
