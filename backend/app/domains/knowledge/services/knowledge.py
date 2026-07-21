"""Knowledge space + source + conversation services."""

from __future__ import annotations

import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.domains.knowledge.models import (
    AIUsageRecord,
    Conversation,
    ConversationSource,
    KnowledgeSource,
    KnowledgeSpace,
    KnowledgeSpaceMember,
    Message,
    MessageCitation,
    SourceStatus,
    SourceType,
    SpaceMemberRole,
)
from app.domains.knowledge.policies.access import require_space_access
from app.domains.knowledge.schemas import (
    CitationResponse,
    ConversationCreate,
    ConversationResponse,
    KnowledgeSpaceCreate,
    KnowledgeSpaceResponse,
    KnowledgeSpaceUpdate,
    MessageResponse,
    SearchHit,
    SourceCreateText,
    SourceResponse,
)
from app.infrastructure.object_storage.local import save_knowledge_file
from app.infrastructure.queue.memory import enqueue_ingestion
from app.ai.vectorstore import delete_by_metadata
from app.models.user import User
from app.schemas.common import PaginatedResponse

class KnowledgeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Spaces ────────────────────────────────────────────────
    async def create_space(self, user: User, body: KnowledgeSpaceCreate) -> KnowledgeSpaceResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        space = KnowledgeSpace(
            tenant_id=user.tenant_id,
            created_by=user.id,
            title=body.title,
            description=body.description,
        )
        self.session.add(space)
        await self.session.flush()
        self.session.add(
            KnowledgeSpaceMember(
                tenant_id=user.tenant_id,
                space_id=space.id,
                user_id=user.id,
                role=SpaceMemberRole.OWNER.value,
            )
        )
        await self.session.flush()
        return KnowledgeSpaceResponse(
            id=space.id,
            tenant_id=space.tenant_id,
            created_by=space.created_by,
            title=space.title,
            description=space.description,
            is_active=space.is_active,
            created_at=space.created_at,
            member_role=SpaceMemberRole.OWNER.value,
            source_count=0,
        )

    async def list_spaces(self, user: User, page: int = 1, size: int = 20) -> PaginatedResponse[KnowledgeSpaceResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        offset = (page - 1) * size
        # Spaces user belongs to OR any space in tenant for admins
        from app.models.user import UserRole
        if user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            filters = [
                KnowledgeSpace.tenant_id == user.tenant_id,
                KnowledgeSpace.is_active == True,  # noqa: E712
            ]
            total_q = await self.session.execute(select(func.count()).select_from(KnowledgeSpace).where(*filters))
            total = total_q.scalar_one()
            result = await self.session.execute(
                select(KnowledgeSpace).where(*filters).order_by(KnowledgeSpace.created_at.desc()).offset(offset).limit(size)
            )
            spaces = list(result.scalars().all())
        else:
            stmt = (
                select(KnowledgeSpace)
                .join(KnowledgeSpaceMember, KnowledgeSpaceMember.space_id == KnowledgeSpace.id)
                .where(
                    KnowledgeSpace.tenant_id == user.tenant_id,
                    KnowledgeSpace.is_active == True,  # noqa: E712
                    KnowledgeSpaceMember.user_id == user.id,
                )
                .order_by(KnowledgeSpace.created_at.desc())
                .offset(offset)
                .limit(size)
            )
            result = await self.session.execute(stmt)
            spaces = list(result.scalars().unique().all())
            count_stmt = (
                select(func.count())
                .select_from(KnowledgeSpace)
                .join(KnowledgeSpaceMember, KnowledgeSpaceMember.space_id == KnowledgeSpace.id)
                .where(
                    KnowledgeSpace.tenant_id == user.tenant_id,
                    KnowledgeSpace.is_active == True,  # noqa: E712
                    KnowledgeSpaceMember.user_id == user.id,
                )
            )
            total = (await self.session.execute(count_stmt)).scalar_one()

        items = []
        for s in spaces:
            sc = await self.session.execute(
                select(func.count()).select_from(KnowledgeSource).where(
                    KnowledgeSource.space_id == s.id,
                    KnowledgeSource.is_active == True,  # noqa: E712
                )
            )
            items.append(
                KnowledgeSpaceResponse(
                    id=s.id,
                    tenant_id=s.tenant_id,
                    created_by=s.created_by,
                    title=s.title,
                    description=s.description,
                    is_active=s.is_active,
                    created_at=s.created_at,
                    source_count=sc.scalar_one(),
                )
            )
        return PaginatedResponse(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if size else 0)

    async def get_space(self, user: User, space_id: uuid.UUID) -> KnowledgeSpaceResponse:
        space, member = await require_space_access(self.session, user, space_id)
        sc = await self.session.execute(
            select(func.count()).select_from(KnowledgeSource).where(
                KnowledgeSource.space_id == space.id,
                KnowledgeSource.is_active == True,  # noqa: E712
            )
        )
        return KnowledgeSpaceResponse(
            id=space.id,
            tenant_id=space.tenant_id,
            created_by=space.created_by,
            title=space.title,
            description=space.description,
            is_active=space.is_active,
            created_at=space.created_at,
            member_role=member.role if member else "ADMIN",
            source_count=sc.scalar_one(),
        )

    async def update_space(self, user: User, space_id: uuid.UUID, body: KnowledgeSpaceUpdate) -> KnowledgeSpaceResponse:
        space, _ = await require_space_access(self.session, user, space_id, min_role=SpaceMemberRole.EDITOR)
        if body.title is not None:
            space.title = body.title
        if body.description is not None:
            space.description = body.description
        await self.session.flush()
        return await self.get_space(user, space_id)

    async def delete_space(self, user: User, space_id: uuid.UUID) -> None:
        space, _ = await require_space_access(self.session, user, space_id, min_role=SpaceMemberRole.OWNER)
        space.is_active = False
        await self.session.flush()

    # ── Sources ───────────────────────────────────────────────
    async def create_text_source(self, user: User, space_id: uuid.UUID, body: SourceCreateText) -> SourceResponse:
        await require_space_access(self.session, user, space_id, min_role=SpaceMemberRole.EDITOR)
        assert user.tenant_id
        source = KnowledgeSource(
            tenant_id=user.tenant_id,
            space_id=space_id,
            created_by=user.id,
            type=body.type if body.type in {t.value for t in SourceType} else SourceType.TEXT.value,
            name=body.name,
            status=SourceStatus.CREATED.value,
            extra_metadata={"raw_text": body.content},
        )
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        enqueue_ingestion(source.id)
        return self._source_resp(source)

    async def create_file_source(
        self,
        user: User,
        space_id: uuid.UUID,
        *,
        name: str,
        source_type: str,
        data: bytes,
        original_filename: str,
        mime_type: str | None,
    ) -> SourceResponse:
        await require_space_access(self.session, user, space_id, min_role=SpaceMemberRole.EDITOR)
        assert user.tenant_id
        source = KnowledgeSource(
            tenant_id=user.tenant_id,
            space_id=space_id,
            created_by=user.id,
            type=source_type,
            name=name,
            status=SourceStatus.UPLOADING.value,
            mime_type=mime_type,
            byte_size=len(data),
        )
        self.session.add(source)
        await self.session.flush()
        key = save_knowledge_file(data, original_filename, str(source.id))
        source.storage_key = key
        source.status = SourceStatus.CREATED.value
        await self.session.flush()
        await self.session.refresh(source)
        enqueue_ingestion(source.id)
        return self._source_resp(source)

    async def list_sources(self, user: User, space_id: uuid.UUID, page: int = 1, size: int = 50) -> PaginatedResponse[SourceResponse]:
        await require_space_access(self.session, user, space_id)
        offset = (page - 1) * size
        filters = [
            KnowledgeSource.space_id == space_id,
            KnowledgeSource.is_active == True,  # noqa: E712
        ]
        total = (await self.session.execute(select(func.count()).select_from(KnowledgeSource).where(*filters))).scalar_one()
        result = await self.session.execute(
            select(KnowledgeSource).where(*filters).order_by(KnowledgeSource.created_at.desc()).offset(offset).limit(size)
        )
        items = [self._source_resp(s) for s in result.scalars().all()]
        return PaginatedResponse(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if size else 0)

    async def get_source(self, user: User, source_id: uuid.UUID) -> SourceResponse:
        source = await self._get_source(user, source_id)
        await require_space_access(self.session, user, source.space_id)
        return self._source_resp(source)

    async def delete_source(self, user: User, source_id: uuid.UUID) -> None:
        source = await self._get_source(user, source_id)
        await require_space_access(self.session, user, source.space_id, min_role=SpaceMemberRole.EDITOR)
        source.is_active = False
        source.status = SourceStatus.DELETED.value
        delete_by_metadata({"source_id": str(source.id)})
        await self.session.flush()

    async def retry_source(self, user: User, source_id: uuid.UUID) -> SourceResponse:
        source = await self._get_source(user, source_id)
        await require_space_access(self.session, user, source.space_id, min_role=SpaceMemberRole.EDITOR)
        source.status = SourceStatus.CREATED.value
        source.error_message = None
        await self.session.flush()
        enqueue_ingestion(source.id)
        return self._source_resp(source)

    # ── Conversations / Chat ──────────────────────────────────
    async def create_conversation(self, user: User, body: ConversationCreate) -> ConversationResponse:
        await require_space_access(self.session, user, body.space_id)
        assert user.tenant_id
        conv = Conversation(
            tenant_id=user.tenant_id,
            space_id=body.space_id,
            created_by=user.id,
            title=body.title or "New conversation",
            scope_type="SOURCES" if body.source_ids else "SPACE",
        )
        self.session.add(conv)
        await self.session.flush()
        for sid in body.source_ids:
            self.session.add(ConversationSource(conversation_id=conv.id, source_id=sid))
        await self.session.flush()
        await self.session.refresh(conv)
        return ConversationResponse(
            id=conv.id,
            tenant_id=conv.tenant_id,
            space_id=conv.space_id,
            created_by=conv.created_by,
            title=conv.title,
            scope_type=conv.scope_type,
            created_at=conv.created_at,
        )

    async def list_conversations(self, user: User, space_id: uuid.UUID | None = None) -> list[ConversationResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        filters = [
            Conversation.tenant_id == user.tenant_id,
            Conversation.created_by == user.id,
            Conversation.is_active == True,  # noqa: E712
        ]
        if space_id:
            await require_space_access(self.session, user, space_id)
            filters.append(Conversation.space_id == space_id)
        result = await self.session.execute(
            select(Conversation).where(*filters).order_by(Conversation.created_at.desc()).limit(100)
        )
        return [
            ConversationResponse(
                id=c.id,
                tenant_id=c.tenant_id,
                space_id=c.space_id,
                created_by=c.created_by,
                title=c.title,
                scope_type=c.scope_type,
                created_at=c.created_at,
            )
            for c in result.scalars().all()
        ]

    async def list_messages(self, user: User, conversation_id: uuid.UUID) -> list[MessageResponse]:
        conv = await self._get_conversation(user, conversation_id)
        if conv.space_id:
            await require_space_access(self.session, user, conv.space_id)
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .options(selectinload(Message.citations))
            .order_by(Message.created_at.asc())
        )
        out: list[MessageResponse] = []
        for m in result.scalars().all():
            out.append(
                MessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    role=m.role,
                    content=m.content,
                    model=m.model,
                    created_at=m.created_at,
                    citations=[
                        CitationResponse(
                            source_id=c.source_id,
                            chunk_id=c.chunk_id,
                            page_number=c.page_number,
                            timestamp_start=c.timestamp_start,
                            timestamp_end=c.timestamp_end,
                            snippet=c.snippet,
                        )
                        for c in m.citations
                    ],
                )
            )
        return out

    async def search(self, user: User, space_id: uuid.UUID, query: str, source_ids: list[uuid.UUID] | None, top_k: int) -> list[SearchHit]:
        await require_space_access(self.session, user, space_id)
        assert user.tenant_id
        accessible = await self._accessible_source_ids(space_id, source_ids)
        from app.ai.retrieval.rag import retrieve
        hits = await retrieve(
            tenant_id=user.tenant_id,
            space_id=space_id,
            query=query,
            accessible_source_ids=accessible,
            top_k=top_k,
        )
        return [
            SearchHit(
                chunk_id=h.chunk_id,
                source_id=h.source_id,
                source_name=h.source_name,
                content=h.content,
                page_number=h.page_number,
                score=h.score,
            )
            for h in hits
        ]

    async def record_usage(
        self,
        user: User,
        *,
        operation_type: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        metadata: dict | None = None,
    ) -> None:
        if not user.tenant_id:
            return
        self.session.add(
            AIUsageRecord(
                tenant_id=user.tenant_id,
                user_id=user.id,
                operation_type=operation_type,
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=0.0,
                extra_metadata=metadata,
            )
        )
        await self.session.flush()

    # ── helpers ───────────────────────────────────────────────
    def _source_resp(self, s: KnowledgeSource) -> SourceResponse:
        return SourceResponse(
            id=s.id,
            tenant_id=s.tenant_id,
            space_id=s.space_id,
            created_by=s.created_by,
            type=s.type,
            name=s.name,
            status=s.status,
            storage_key=s.storage_key,
            mime_type=s.mime_type,
            byte_size=s.byte_size,
            error_message=s.error_message,
            created_at=s.created_at,
        )

    async def _get_source(self, user: User, source_id: uuid.UUID) -> KnowledgeSource:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        result = await self.session.execute(
            select(KnowledgeSource).where(
                KnowledgeSource.id == source_id,
                KnowledgeSource.tenant_id == user.tenant_id,
                KnowledgeSource.is_active == True,  # noqa: E712
            )
        )
        source = result.scalar_one_or_none()
        if not source:
            raise NotFoundException("Source not found")
        return source

    async def _get_conversation(self, user: User, conversation_id: uuid.UUID) -> Conversation:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.tenant_id == user.tenant_id,
                Conversation.is_active == True,  # noqa: E712
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise NotFoundException("Conversation not found")
        return conv

    async def _accessible_source_ids(
        self, space_id: uuid.UUID, source_ids: list[uuid.UUID] | None
    ) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(KnowledgeSource.id).where(
                KnowledgeSource.space_id == space_id,
                KnowledgeSource.is_active == True,  # noqa: E712
                KnowledgeSource.status == SourceStatus.READY.value,
            )
        )
        ready = set(result.scalars().all())
        if source_ids:
            return [s for s in source_ids if s in ready]
        return list(ready)
