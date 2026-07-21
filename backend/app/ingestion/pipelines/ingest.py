"""Ingestion entrypoint — LangGraph pipeline (LangChain load/split/embed)."""

from app.ai.workflows.ingestion.graph import run_ingestion

__all__ = ["run_ingestion"]
