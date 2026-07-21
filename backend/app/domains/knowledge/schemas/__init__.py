"""Knowledge domain Pydantic schemas — split by concern, re-exported here."""

from app.domains.knowledge.schemas.conversation import (
    CitationResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.domains.knowledge.schemas.search import SearchHit, SearchRequest
from app.domains.knowledge.schemas.source import SourceCreateText, SourceResponse
from app.domains.knowledge.schemas.space import (
    KnowledgeSpaceCreate,
    KnowledgeSpaceResponse,
    KnowledgeSpaceUpdate,
)

__all__ = [
    "KnowledgeSpaceCreate",
    "KnowledgeSpaceUpdate",
    "KnowledgeSpaceResponse",
    "SourceCreateText",
    "SourceResponse",
    "ConversationCreate",
    "ConversationResponse",
    "CitationResponse",
    "MessageResponse",
    "MessageCreate",
    "SearchRequest",
    "SearchHit",
]
