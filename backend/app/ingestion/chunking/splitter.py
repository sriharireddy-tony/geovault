"""LangChain RecursiveCharacterTextSplitter for document chunking."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def split_documents(docs: list[Document]) -> list[Document]:
    """Split LangChain Documents into overlapping chunks (preserves metadata)."""
    if not docs:
        return []
    splitter = get_text_splitter()
    return splitter.split_documents(docs)
