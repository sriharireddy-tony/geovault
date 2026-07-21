"""Knowledge domain enums."""

from __future__ import annotations

import enum


class SourceType(str, enum.Enum):
    TEXT = "TEXT"
    TXT = "TXT"
    MARKDOWN = "MARKDOWN"
    PDF = "PDF"
    DOCX = "DOCX"
    PPTX = "PPTX"
    CSV = "CSV"
    XLSX = "XLSX"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    WEB_URL = "WEB_URL"
    YOUTUBE = "YOUTUBE"


class SourceStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    EXTRACTING = "EXTRACTING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"


class SpaceMemberRole(str, enum.Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"
