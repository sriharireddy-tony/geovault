"""LangGraph nodes for production RAG chat — LangChain LCEL shortcuts."""

from __future__ import annotations

import uuid
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from app.ai.evaluation.rag_eval import evaluate_answer
from app.ai.guardrails.checks import check_input, check_output, redact_pii
from app.ai.llm.langchain_factory import get_chat_model
from app.ai.prompts.rag import format_docs_for_context, get_rag_prompt
from app.ai.retrieval.rag import retrieve
from app.ai.workflows.chat.state import ChatGraphState
from app.core.config import get_settings


async def node_input_guardrails(state: ChatGraphState) -> dict[str, Any]:
    settings = get_settings()
    if not settings.ENABLE_GUARDRAILS:
        return {"blocked": False, "status": "guardrails_skipped"}
    result = check_input(state.get("question") or "")
    if not result.ok and settings.GUARDRAILS_BLOCK_ON_FAIL:
        msg = "Your message was blocked by safety guardrails. Please rephrase."
        return {
            "blocked": True,
            "block_reason": ",".join(result.reasons),
            "answer": msg,
            "status": "blocked",
            "tokens": [msg],
        }
    return {"question": result.sanitized_text, "blocked": False, "status": "input_ok"}


async def node_retrieve(state: ChatGraphState) -> dict[str, Any]:
    if state.get("blocked"):
        return {"status": "skipped_retrieve"}
    source_ids = [uuid.UUID(s) for s in (state.get("accessible_source_ids") or [])]
    chunks = await retrieve(
        tenant_id=uuid.UUID(state["tenant_id"]),
        space_id=uuid.UUID(state["space_id"]),
        query=state["question"],
        accessible_source_ids=source_ids,
    )
    contexts = [
        {
            "source_name": c.source_name,
            "page_number": c.page_number,
            "content": c.content,
            "source_id": c.source_id,
            "chunk_id": c.chunk_id,
        }
        for c in chunks
    ]
    return {"contexts": contexts, "status": "retrieved"}


async def node_generate(state: ChatGraphState) -> dict[str, Any]:
    if state.get("blocked"):
        return {"status": "skipped_generate"}

    contexts = state.get("contexts") or []
    settings = get_settings()
    provider = settings.LLM_PROVIDER
    model = get_chat_model()

    if not contexts:
        answer = (
            "I do not have enough information in the selected knowledge sources "
            "to answer that. Please upload or select relevant documents."
        )
        return {
            "answer": answer,
            "tokens": [answer],
            "citations": [],
            "model": getattr(model, "model", None) or getattr(model, "model_name", provider),
            "provider": provider,
            "status": "no_context",
        }

    history_msgs = []
    for h in (state.get("history") or [])[-settings.RAG_HISTORY_LIMIT :]:
        if h.get("role") == "user":
            history_msgs.append(HumanMessage(content=h["content"]))
        elif h.get("role") == "assistant":
            history_msgs.append(AIMessage(content=h["content"]))

    # LangChain LCEL shortcut: prompt | model | StrOutputParser
    chain = get_rag_prompt() | model | StrOutputParser()
    answer = (
        await chain.ainvoke(
            {
                "history": history_msgs,
                "context": format_docs_for_context(contexts),
                "question": state["question"],
            }
        )
    ).strip()

    citations = [
        {
            "source_id": c["source_id"],
            "source_name": c.get("source_name"),
            "chunk_id": c.get("chunk_id"),
            "page_number": c.get("page_number"),
            "snippet": (c.get("content") or "")[:280],
        }
        for c in contexts[:8]
    ]
    return {
        "answer": answer,
        "tokens": [answer],
        "citations": citations,
        "model": getattr(model, "model", None) or getattr(model, "model_name", provider),
        "provider": provider,
        "status": "generated",
    }


async def node_output_guardrails(state: ChatGraphState) -> dict[str, Any]:
    settings = get_settings()
    if not settings.ENABLE_GUARDRAILS or state.get("blocked"):
        return {"status": state.get("status") or "done"}
    result = check_output(state.get("answer") or "")
    text = redact_pii(result.sanitized_text)
    if not result.ok and settings.GUARDRAILS_BLOCK_ON_FAIL:
        msg = "The generated answer was blocked by safety guardrails."
        return {"answer": msg, "tokens": [msg], "status": "output_blocked"}
    return {"answer": text, "status": "output_ok"}


async def node_evaluate(state: ChatGraphState) -> dict[str, Any]:
    settings = get_settings()
    if not settings.ENABLE_EVALUATION or state.get("blocked"):
        return {}
    contexts = [c.get("content") or "" for c in (state.get("contexts") or [])]
    scores = evaluate_answer(
        question=state.get("question") or "",
        answer=state.get("answer") or "",
        contexts=contexts,
        citation_count=len(state.get("citations") or []),
    )
    return {
        "eval_scores": {
            "groundedness": scores.groundedness,
            "citation_coverage": scores.citation_coverage,
            "has_context": scores.has_context,
            "notes": scores.notes,
        },
        "status": "evaluated",
    }
