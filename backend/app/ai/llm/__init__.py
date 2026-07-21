"""LLM package — LangChain chat model factory (Ollama / OpenAI / Gemini)."""

from app.ai.llm.langchain_factory import get_chat_model, reset_chat_model

__all__ = ["get_chat_model", "reset_chat_model"]
