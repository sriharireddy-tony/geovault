"""LangGraph chat RAG state."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class ChatGraphState(TypedDict, total=False):
    # identity / tenancy
    tenant_id: str
    user_id: str
    space_id: str
    conversation_id: str
    accessible_source_ids: list[str]

    # dialog
    question: str
    history: list[dict[str, str]]  # {role, content}
    answer: str
    tokens: Annotated[list[str], operator.add]

    # retrieval
    contexts: list[dict[str, Any]]
    citations: list[dict[str, Any]]

    # control
    blocked: bool
    block_reason: str
    status: str
    eval_scores: dict[str, Any]
    model: str
    provider: str
    error: str
