"""LangGraph ingestion workflow: load → split → embed → index.

Pure LangChain loaders/splitters/embeddings + tenant-aware vector upsert.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.ai.vectorstore import delete_by_metadata, get_lc_vectorstore
from app.core.database import engine
from app.domains.knowledge.models import (
    ContentBlock,
    DocumentChunk,
    IngestionJob,
    KnowledgeSource,
    SourceStatus,
    SourceType,
)
from app.infrastructure.object_storage.local import resolve_storage_path
from app.ingestion.chunking.splitter import split_documents
from app.ingestion.loaders import load_documents

logger = logging.getLogger(__name__)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class IngestState(TypedDict, total=False):
    source_id: str
    tenant_id: str
    space_id: str
    source_name: str
    source_type: str
    documents: list[Document]
    chunks: list[Document]
    status: str
    error: str
    chunk_count: int


async def node_load(state: IngestState) -> dict[str, Any]:
    source_id = uuid.UUID(state["source_id"])
    async with SessionLocal() as session:
        source = await _get_source(session, source_id)
        if not source:
            return {"error": "source_not_found", "status": "FAILED"}
        await _set_status(session, source, SourceStatus.EXTRACTING.value)
        await session.commit()

        docs = _load_for_source(source)
        return {
            "tenant_id": str(source.tenant_id),
            "space_id": str(source.space_id),
            "source_name": source.name,
            "source_type": source.type,
            "documents": docs,
            "status": "EXTRACTING",
        }


async def node_split(state: IngestState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    source_id = uuid.UUID(state["source_id"])
    async with SessionLocal() as session:
        source = await _get_source(session, source_id)
        if source:
            await _set_status(session, source, SourceStatus.CHUNKING.value)
            await session.commit()

    chunks = split_documents(state.get("documents") or [])
    return {"chunks": chunks, "status": "CHUNKING", "chunk_count": len(chunks)}


async def node_embed_index(state: IngestState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    source_id = uuid.UUID(state["source_id"])
    chunks = state.get("chunks") or []
    docs = state.get("documents") or []

    async with SessionLocal() as session:
        source = await _get_source(session, source_id)
        if not source:
            return {"error": "source_not_found", "status": "FAILED"}

        # Clear previous derived data
        await session.execute(delete(DocumentChunk).where(DocumentChunk.source_id == source.id))
        await session.execute(delete(ContentBlock).where(ContentBlock.source_id == source.id))
        delete_by_metadata({"source_id": str(source.id)})
        store = get_lc_vectorstore()

        for i, d in enumerate(docs):
            session.add(
                ContentBlock(
                    tenant_id=source.tenant_id,
                    source_id=source.id,
                    content=d.page_content,
                    content_type=str(d.metadata.get("content_type") or "TEXT"),
                    page_number=_page(d.metadata),
                    section=d.metadata.get("section") or d.metadata.get("sheet"),
                    ordinal=i,
                    extra_metadata={k: v for k, v in d.metadata.items() if isinstance(v, (str, int, float, bool))},
                )
            )
        await session.flush()

        await _set_status(session, source, SourceStatus.EMBEDDING.value)
        await session.commit()
        await session.refresh(source)
        await _set_status(session, source, SourceStatus.INDEXING.value)

        chunk_rows: list[DocumentChunk] = []
        lc_docs: list[Document] = []
        ids: list[str] = []
        for idx, c in enumerate(chunks):
            row = DocumentChunk(
                tenant_id=source.tenant_id,
                space_id=source.space_id,
                source_id=source.id,
                content=c.page_content,
                token_count=max(1, len(c.page_content) // 4),
                chunk_index=idx,
                page_number=_page(c.metadata),
                section=c.metadata.get("section") or c.metadata.get("sheet"),
                extra_metadata={k: v for k, v in c.metadata.items() if isinstance(v, (str, int, float, bool))},
            )
            session.add(row)
            chunk_rows.append(row)
        await session.flush()

        for row in chunk_rows:
            ids.append(str(row.id))
            lc_docs.append(
                Document(
                    page_content=row.content,
                    metadata={
                        "tenant_id": str(source.tenant_id),
                        "space_id": str(source.space_id),
                        "source_id": str(source.id),
                        "source_name": source.name,
                        "chunk_id": str(row.id),
                        "id": str(row.id),
                        "page_number": row.page_number if row.page_number is not None else -1,
                        "source_type": source.type,
                    },
                )
            )

        # LangChain shortcut: vectorstore.add_documents embeds + indexes
        store.add_documents(lc_docs, ids=ids)

        await _set_status(session, source, SourceStatus.READY.value)
        session.add(
            IngestionJob(
                tenant_id=source.tenant_id,
                source_id=source.id,
                status=SourceStatus.READY.value,
                attempts=1,
                idempotency_key=f"ingest:{source.id}:{uuid.uuid4()}",
                started_at=datetime.now(UTC),
                finished_at=datetime.now(UTC),
            )
        )
        await session.commit()
        return {"status": "READY", "chunk_count": len(chunk_rows)}


def build_ingestion_graph():
    g = StateGraph(IngestState)
    g.add_node("load", node_load)
    g.add_node("split", node_split)
    g.add_node("embed_index", node_embed_index)
    g.add_edge(START, "load")
    g.add_edge("load", "split")
    g.add_edge("split", "embed_index")
    g.add_edge("embed_index", END)
    return g.compile()


_INGEST_GRAPH = None


def get_ingestion_graph():
    global _INGEST_GRAPH
    if _INGEST_GRAPH is None:
        _INGEST_GRAPH = build_ingestion_graph()
    return _INGEST_GRAPH


async def run_ingestion(source_id: uuid.UUID) -> None:
    """Public entry — enqueue target for KnowledgeService."""
    try:
        result = await get_ingestion_graph().ainvoke({"source_id": str(source_id)})
        if result.get("error") or result.get("status") == "FAILED":
            await _mark_failed(source_id, result.get("error") or "ingestion_failed")
        else:
            logger.info(
                "LangGraph ingestion complete for %s (%s chunks)",
                source_id,
                result.get("chunk_count"),
            )
    except Exception as exc:
        logger.exception("LangGraph ingestion failed for %s", source_id)
        await _mark_failed(source_id, str(exc)[:2000])


def _load_for_source(source: KnowledgeSource) -> list[Document]:
    if source.type == SourceType.TEXT.value:
        raw = (source.extra_metadata or {}).get("raw_text") or ""
        return load_documents(source_type="TEXT", raw_text=raw)

    if not source.storage_key:
        raise ValueError("Source has no storage_key")
    path = resolve_storage_path(source.storage_key)
    if not path.is_file():
        path = Path(source.storage_key.lstrip("/"))
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {source.storage_key}")
    return load_documents(source_type=source.type, path=path)


def _page(meta: dict) -> int | None:
    if meta.get("page_number") is not None:
        try:
            return int(meta["page_number"])
        except Exception:
            return None
    if meta.get("page") is not None:
        try:
            return int(meta["page"]) + 1
        except Exception:
            return None
    return None


async def _get_source(session: AsyncSession, source_id: uuid.UUID) -> KnowledgeSource | None:
    result = await session.execute(select(KnowledgeSource).where(KnowledgeSource.id == source_id))
    return result.scalar_one_or_none()


async def _set_status(session: AsyncSession, source: KnowledgeSource, status: str, error: str | None = None) -> None:
    source.status = status
    source.error_message = error
    await session.flush()


async def _mark_failed(source_id: uuid.UUID, message: str) -> None:
    async with SessionLocal() as session:
        source = await _get_source(session, source_id)
        if source:
            source.status = SourceStatus.FAILED.value
            source.error_message = message
            await session.commit()
