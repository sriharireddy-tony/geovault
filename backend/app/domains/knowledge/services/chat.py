"""Streaming RAG chat via LangGraph + persistent per-user memory."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.workflows.chat.graph import run_chat_graph
from app.core.config import get_settings
from app.domains.knowledge.models import ConversationSource, Message, MessageCitation
from app.domains.knowledge.policies.access import require_space_access
from app.domains.knowledge.services.knowledge import KnowledgeService
from app.models.user import User


async def stream_chat_response(
    session: AsyncSession,
    user: User,
    conversation_id: uuid.UUID,
    question: str,
    source_ids: list[uuid.UUID] | None = None,
) -> AsyncIterator[str]:
    """Yield NDJSON events. Conversation history is loaded from DB (survives re-login)."""
    svc = KnowledgeService(session)
    conv = await svc._get_conversation(user, conversation_id)
    if not conv.space_id:
        yield _sse({"type": "error", "detail": "Conversation has no knowledge space"})
        return

    await require_space_access(session, user, conv.space_id)
    assert user.tenant_id

    # Load prior messages for this user+tenant conversation (persistent memory)
    settings = get_settings()
    hist_q = await session.execute(
        select(Message)
        .where(Message.conversation_id == conv.id, Message.tenant_id == user.tenant_id)
        .order_by(Message.created_at.asc())
    )
    prior = list(hist_q.scalars().all())
    history = [{"role": m.role, "content": m.content} for m in prior[-settings.RAG_HISTORY_LIMIT :]]

    # Persist the new user turn
    user_msg = Message(
        tenant_id=user.tenant_id,
        conversation_id=conv.id,
        role="user",
        content=question,
    )
    session.add(user_msg)
    await session.flush()

    scoped = source_ids
    if scoped is None:
        cs = await session.execute(
            select(ConversationSource.source_id).where(ConversationSource.conversation_id == conv.id)
        )
        linked = list(cs.scalars().all())
        scoped = linked or None

    accessible = await svc._accessible_source_ids(conv.space_id, scoped)
    yield _sse({"type": "status", "detail": "running_langgraph"})

    result = await run_chat_graph(
        {
            "tenant_id": str(user.tenant_id),
            "user_id": str(user.id),
            "space_id": str(conv.space_id),
            "conversation_id": str(conv.id),
            "accessible_source_ids": [str(s) for s in accessible],
            "question": question,
            "history": history,
            "tokens": [],
            "contexts": [],
            "citations": [],
            "blocked": False,
        }
    )

    answer = result.get("answer") or ""
    citations = result.get("citations") or []
    model = result.get("model") or get_settings().LLM_PROVIDER
    provider = result.get("provider") or get_settings().LLM_PROVIDER

    # Stream answer as tokens (graph currently returns full answer)
    if answer:
        # chunk for smoother UI
        step = 80
        for i in range(0, len(answer), step):
            yield _sse({"type": "token", "content": answer[i : i + step]})
    else:
        answer = "No response generated."
        yield _sse({"type": "token", "content": answer})

    assistant = Message(
        tenant_id=user.tenant_id,
        conversation_id=conv.id,
        role="assistant",
        content=answer,
        model=str(model),
        input_tokens=0,
        output_tokens=max(1, len(answer) // 4),
    )
    session.add(assistant)
    await session.flush()

    citations_payload = []
    for c in citations:
        try:
            sid = uuid.UUID(str(c["source_id"]))
        except Exception:
            continue
        chunk_id = None
        if c.get("chunk_id"):
            try:
                chunk_id = uuid.UUID(str(c["chunk_id"]))
            except Exception:
                chunk_id = None
        session.add(
            MessageCitation(
                message_id=assistant.id,
                source_id=sid,
                chunk_id=chunk_id,
                page_number=c.get("page_number"),
                snippet=c.get("snippet"),
            )
        )
        citations_payload.append(c)

    await svc.record_usage(
        user,
        operation_type="langgraph_rag_chat",
        model=str(model),
        provider=str(provider),
        input_tokens=0,
        output_tokens=assistant.output_tokens,
        metadata={
            "conversation_id": str(conv.id),
            "eval": result.get("eval_scores"),
            "blocked": result.get("blocked", False),
        },
    )
    await session.commit()
    yield _sse(
        {
            "type": "done",
            "message_id": str(assistant.id),
            "citations": citations_payload,
            "eval": result.get("eval_scores"),
            "status": result.get("status"),
        }
    )


def _sse(payload: dict) -> str:
    return json.dumps(payload, default=str) + "\n"
