import uuid

from pydantic import BaseModel, ConfigDict, Field


class PreferenceUpdate(BaseModel):
    theme_mode: str = Field(default="system", pattern="^(light|dark|system)$")
    theme_color: str = Field(default="#6366f1", max_length=20)


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    theme_mode: str
    theme_color: str
