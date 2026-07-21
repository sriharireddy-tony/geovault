"""Shared helpers for LangChain document loaders."""

from __future__ import annotations

from langchain_core.documents import Document


def tag_docs(docs: list[Document], *, source_type: str, content_type: str) -> list[Document]:
    for d in docs:
        d.metadata["source_type"] = source_type
        d.metadata["content_type"] = content_type
    return docs
