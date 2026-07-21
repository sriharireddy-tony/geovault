"""PDF loaders."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.loaders._common import tag_docs


def load_pdf(path: Path) -> list[Document]:
    from langchain_community.document_loaders import PyPDFLoader

    docs = PyPDFLoader(str(path)).load()
    for d in docs:
        page = d.metadata.get("page")
        if page is not None:
            d.metadata["page_number"] = int(page) + 1
    return tag_docs(docs, source_type="PDF", content_type="TEXT")
