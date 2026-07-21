"""Local file storage utility. Replace with S3 for production."""

import uuid
from pathlib import Path

MEDIA_ROOT = Path("media")
AUDIO_DIR = MEDIA_ROOT / "audios"
IMAGE_DIR = MEDIA_ROOT / "images"
VIDEO_DIR = MEDIA_ROOT / "videos"

for _d in (AUDIO_DIR, IMAGE_DIR, VIDEO_DIR):
    _d.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".wma", ".mp4"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".tiff", ".tif"}
ALLOWED_VIDEO = {".mp4", ".mov", ".webm", ".avi", ".mkv", ".flv", ".wmv", ".m4v"}


def _ext(filename: str) -> str:
    return Path(filename).suffix.lower()


def save_audio_file(audio_bytes: bytes, extension: str = "wav") -> str:
    filename = f"{uuid.uuid4()}.{extension.lstrip('.')}"
    filepath = AUDIO_DIR / filename
    filepath.write_bytes(audio_bytes)
    return f"/media/audios/{filename}"


def save_uploaded_audio(data: bytes, original_name: str) -> str:
    ext = _ext(original_name) or ".wav"
    filename = f"{uuid.uuid4()}{ext}"
    (AUDIO_DIR / filename).write_bytes(data)
    return f"/media/audios/{filename}"


def save_uploaded_image(data: bytes, original_name: str) -> str:
    ext = _ext(original_name) or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    (IMAGE_DIR / filename).write_bytes(data)
    return f"/media/images/{filename}"


def save_uploaded_video(data: bytes, original_name: str) -> str:
    ext = _ext(original_name) or ".mp4"
    filename = f"{uuid.uuid4()}{ext}"
    (VIDEO_DIR / filename).write_bytes(data)
    return f"/media/videos/{filename}"
