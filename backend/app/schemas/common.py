import uuid

from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")


class CreatorInfo(BaseModel):
    id: uuid.UUID
    name: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    pages: int


class MessageResponse(BaseModel):
    detail: str
