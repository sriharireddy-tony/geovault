"""LangChain embeddings factory — Ollama / OpenAI / Gemini via EMBEDDING_PROVIDER."""

from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings

from app.core.config import get_settings
from app.core.exceptions import BadRequestException


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER.lower().strip()

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBED_MODEL,
        )

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise BadRequestException("OPENAI_API_KEY is not configured")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_EMBED_MODEL,
        )

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise BadRequestException("GEMINI_API_KEY is not configured")
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError as exc:
            raise BadRequestException(
                "Install langchain-google-genai to use Gemini embeddings"
            ) from exc
        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_EMBED_MODEL,
        )

    raise BadRequestException(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def reset_embeddings() -> None:
    get_embeddings.cache_clear()
