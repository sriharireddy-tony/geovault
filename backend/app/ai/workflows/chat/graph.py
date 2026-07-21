"""LangGraph RAG chatbot workflow.

Flow:
  input_guardrails → retrieve → generate → output_guardrails → evaluate → END
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.ai.observability.langsmith import configure_langsmith
from app.ai.workflows.chat.nodes.rag_nodes import (
    node_evaluate,
    node_generate,
    node_input_guardrails,
    node_output_guardrails,
    node_retrieve,
)
from app.ai.workflows.chat.state import ChatGraphState


@lru_cache
def get_chat_graph():
    configure_langsmith()
    graph = StateGraph(ChatGraphState)
    graph.add_node("input_guardrails", node_input_guardrails)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("generate", node_generate)
    graph.add_node("output_guardrails", node_output_guardrails)
    graph.add_node("evaluate", node_evaluate)

    graph.add_edge(START, "input_guardrails")
    graph.add_edge("input_guardrails", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "output_guardrails")
    graph.add_edge("output_guardrails", "evaluate")
    graph.add_edge("evaluate", END)
    return graph.compile()


async def run_chat_graph(initial: ChatGraphState) -> ChatGraphState:
    app = get_chat_graph()
    result = await app.ainvoke(initial)
    return result  # type: ignore[return-value]
