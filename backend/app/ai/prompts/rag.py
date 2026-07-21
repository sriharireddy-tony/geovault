"""LangChain ChatPromptTemplate for RAG generation."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

RAG_SYSTEM_PROMPT = """You are a knowledge assistant for a multi-tenant SaaS platform.
Answer ONLY using the provided context excerpts.
If the context is insufficient, say clearly that you do not have enough information.
Do not invent facts. Cite sources using [n] markers that match the context numbering.
Be concise and accurate."""

RAG_HUMAN_TEMPLATE = """Context:
{context}

Question: {question}

Answer with citations like [1], [2] where applicable."""


def get_rag_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            MessagesPlaceholder("history", optional=True),
            ("human", RAG_HUMAN_TEMPLATE),
        ]
    )


def format_docs_for_context(contexts: list[dict]) -> str:
    """LangChain-style document formatting with citation indices."""
    parts: list[str] = []
    for i, ctx in enumerate(contexts, start=1):
        cite = f"[Source: {ctx.get('source_name', 'unknown')}"
        if ctx.get("page_number"):
            cite += f", page {ctx['page_number']}"
        cite += "]"
        parts.append(f"[{i}] {cite}\n{ctx.get('content', '')}")
    return "\n\n".join(parts)
