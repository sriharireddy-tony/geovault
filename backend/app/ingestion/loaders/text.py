"""Plain text / markdown loaders."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.loaders._common import tag_docs


def load_inline_text(raw_text: str | None) -> list[Document]:
    text = (raw_text or "").strip()
    if not text:
        return []
    return [Document(page_content=text, metadata={"source_type": "TEXT", "content_type": "TEXT"})]


def load_text_file(path: Path, *, source_type: str) -> list[Document]:
    from langchain_community.document_loaders import TextLoader

    docs = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
    content_type = "MARKDOWN" if source_type == "MARKDOWN" else "TEXT"
    return tag_docs(docs, source_type=source_type, content_type=content_type)
