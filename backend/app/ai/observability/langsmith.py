"""Configure LangSmith tracing from settings (no-op when disabled)."""

from __future__ import annotations

import os

from app.core.config import get_settings


def configure_langsmith() -> None:
    settings = get_settings()
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    else:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
