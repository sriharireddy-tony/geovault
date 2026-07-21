"""LangChain VectorStore adapters — Chroma (preferred) + local cosine fallback.

Gives framework shortcuts: add_documents(), similarity_search(), as_retriever().
"""

from __future__ import annotations

import json
import logging
import math
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from app.ai.embeddings.langchain_factory import get_embeddings
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LocalCosineVectorStore(VectorStore):
    """Persisted cosine vector store implementing the LangChain VectorStore API."""

    def __init__(self, embedding: Embeddings, persist_dir: str) -> None:
        self._embedding = embedding
        self.root = Path(persist_dir) / "lc_local_vectors"
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        self._index: dict[str, dict[str, Any]] = {}
        if self.index_path.exists():
            self._index = json.loads(self.index_path.read_text(encoding="utf-8"))

    @property
    def embeddings(self) -> Embeddings:
        return self._embedding

    def _save(self) -> None:
        self.index_path.write_text(json.dumps(self._index), encoding="utf-8")

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: list[dict] | None = None,
        *,
        ids: list[str] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        text_list = list(texts)
        metas = metadatas or [{} for _ in text_list]
        id_list = ids or [str(uuid.uuid4()) for _ in text_list]
        vectors = self._embedding.embed_documents(text_list)
        for i, text in enumerate(text_list):
            self._index[id_list[i]] = {
                "document": text,
                "embedding": vectors[i],
                "metadata": metas[i],
            }
        self._save()
        return id_list

    def similarity_search(
        self, query: str, k: int = 4, filter: dict[str, Any] | None = None, **kwargs: Any
    ) -> list[Document]:
        docs_scores = self.similarity_search_with_score(query, k=k, filter=filter, **kwargs)
        return [d for d, _ in docs_scores]

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter: dict[str, Any] | None = None, **kwargs: Any
    ) -> list[tuple[Document, float]]:
        q = self._embedding.embed_query(query)
        scored: list[tuple[float, Document]] = []
        for vid, row in self._index.items():
            meta = row.get("metadata") or {}
            if filter and not _match_filter(meta, filter):
                continue
            score = _cosine(q, row["embedding"])
            doc = Document(page_content=row.get("document") or "", metadata={**meta, "id": vid})
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        # LangChain often treats lower distance as better; we return (doc, distance)
        return [(doc, 1.0 - score) for score, doc in scored[:k]]

    def delete(self, ids: list[str] | None = None, **kwargs: Any) -> bool | None:
        filter = kwargs.get("filter")
        if ids:
            for i in ids:
                self._index.pop(i, None)
        elif filter:
            to_del = [vid for vid, row in self._index.items() if _match_filter(row.get("metadata") or {}, filter)]
            for vid in to_del:
                self._index.pop(vid, None)
        self._save()
        return True

    @classmethod
    def from_texts(
        cls,
        texts: list[str],
        embedding: Embeddings,
        metadatas: list[dict] | None = None,
        *,
        persist_dir: str = "chroma_data",
        **kwargs: Any,
    ) -> LocalCosineVectorStore:
        store = cls(embedding=embedding, persist_dir=persist_dir)
        store.add_texts(texts, metadatas=metadatas)
        return store


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _match_filter(meta: dict[str, Any], filt: dict[str, Any]) -> bool:
    if "$and" in filt:
        return all(_match_filter(meta, c) for c in filt["$and"])
    for key, expected in filt.items():
        if key.startswith("$"):
            continue
        actual = meta.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


@lru_cache
def get_lc_vectorstore() -> VectorStore:
    """Return a LangChain VectorStore (Chroma if available, else local cosine)."""
    settings = get_settings()
    embeddings = get_embeddings()
    mode = settings.VECTOR_STORE.lower().strip()

    if mode != "local":
        try:
            try:
                from langchain_chroma import Chroma
            except ImportError:
                from langchain_community.vectorstores import Chroma

            store = Chroma(
                collection_name=settings.CHROMA_COLLECTION,
                embedding_function=embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
            logger.info("Using LangChain Chroma vector store")
            return store
        except Exception as exc:
            if mode == "chroma":
                raise
            logger.warning("LangChain Chroma unavailable (%s) — using LocalCosineVectorStore", exc)

    return LocalCosineVectorStore(embedding=embeddings, persist_dir=settings.CHROMA_PERSIST_DIR)


def reset_lc_vectorstore() -> None:
    get_lc_vectorstore.cache_clear()


def delete_by_metadata(filter: dict[str, Any]) -> None:
    """Delete vectors matching metadata filter (Chroma + local cosine)."""
    store = get_lc_vectorstore()
    try:
        store.delete(filter=filter)
    except TypeError:
        # Older Chroma wrappers accept `where=` instead of `filter=`
        store.delete(where=filter)  # type: ignore[call-arg]
    except Exception as exc:
        logger.warning("Vector delete skipped: %s", exc)
