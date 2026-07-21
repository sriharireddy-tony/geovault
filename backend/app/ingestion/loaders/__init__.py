"""Knowledge source loaders (LangChain) — one module per media/document family."""

from app.ingestion.loaders.dispatcher import load_documents

__all__ = ["load_documents"]
