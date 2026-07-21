"""Tenant-aware RAG retrieval via LangChain VectorStore.as_retriever()."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from langchain_core.documents import Document

from app.ai.vectorstore import get_lc_vectorstore
from app.core.config import get_settings


@dataclass
class RetrievedChunk:
    chunk_id: str
    source_id: str
    source_name: str
    content: str
    page_number: int | None
    score: float | None


def _tenant_filter(
    tenant_id: uuid.UUID,
    space_id: uuid.UUID,
    accessible_source_ids: list[uuid.UUID],
) -> dict:
    return {
        "$and": [
            {"tenant_id": str(tenant_id)},
            {"space_id": str(space_id)},
            {"source_id": {"$in": [str(s) for s in accessible_source_ids]}},
        ]
    }


async def retrieve(
    *,
    tenant_id: uuid.UUID,
    space_id: uuid.UUID,
    query: str,
    accessible_source_ids: list[uuid.UUID],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    if not accessible_source_ids:
        return []

    k = top_k or get_settings().RAG_TOP_K
    filt = _tenant_filter(tenant_id, space_id, accessible_source_ids)
    store = get_lc_vectorstore()

    # LangChain shortcut: as_retriever + ainvoke
    retriever = store.as_retriever(search_kwargs={"k": k, "filter": filt})
    try:
        docs: list[Document] = await retriever.ainvoke(query)
    except Exception:
        # Some vector stores expect sync filter kwargs slightly differently
        docs = store.similarity_search(query, k=k, filter=filt)

    results: list[RetrievedChunk] = []
    for d in docs:
        meta = d.metadata or {}
        page = meta.get("page_number")
        results.append(
            RetrievedChunk(
                chunk_id=str(meta.get("id") or meta.get("chunk_id") or ""),
                source_id=str(meta.get("source_id") or ""),
                source_name=str(meta.get("source_name") or ""),
                content=d.page_content,
                page_number=None if page in (None, -1, "-1") else int(page),
                score=None,
            )
        )
    return results
