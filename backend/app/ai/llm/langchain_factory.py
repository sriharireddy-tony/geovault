"""LangChain chat model factory — Ollama / OpenAI / Gemini via LLM_PROVIDER."""

from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import get_settings
from app.core.exceptions import BadRequestException


@lru_cache
def get_chat_model() -> BaseChatModel:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower().strip()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_CHAT_MODEL,
            temperature=0.2,
        )

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise BadRequestException("OPENAI_API_KEY is not configured")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.2,
        )

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise BadRequestException("GEMINI_API_KEY is not configured")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:
            raise BadRequestException(
                "Install langchain-google-genai to use Gemini with LangChain"
            ) from exc
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_CHAT_MODEL,
            temperature=0.2,
        )

    raise BadRequestException(f"Unsupported LLM_PROVIDER: {provider}")


def reset_chat_model() -> None:
    get_chat_model.cache_clear()
