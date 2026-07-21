"""Audio loaders (transcription stub — wire STT later)."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.loaders._common import tag_docs


def load_audio(path: Path) -> list[Document]:
    """Return a searchable stub until a transcription pipeline is configured."""
    stub = (
        f"Audio file: {path.name}. Transcription not yet configured. "
        "Wire a speech-to-text provider to extract spoken content."
    )
    docs = [
        Document(
            page_content=stub,
            metadata={"format": "audio", "transcribed": False, "filename": path.name},
        )
    ]
    return tag_docs(docs, source_type="AUDIO", content_type="AUDIO_TRANSCRIPT")
