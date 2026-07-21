"""Knowledge space access policies."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.domains.knowledge.models import KnowledgeSpace, KnowledgeSpaceMember, SpaceMemberRole
from app.models.user import User, UserRole


async def require_space_access(
    session: AsyncSession,
    user: User,
    space_id: uuid.UUID,
    *,
    min_role: SpaceMemberRole = SpaceMemberRole.VIEWER,
) -> tuple[KnowledgeSpace, KnowledgeSpaceMember | None]:
    if not user.tenant_id:
        raise ForbiddenException("No tenant context")

    result = await session.execute(
        select(KnowledgeSpace).where(
            KnowledgeSpace.id == space_id,
            KnowledgeSpace.tenant_id == user.tenant_id,
            KnowledgeSpace.is_active == True,  # noqa: E712
        )
    )
    space = result.scalar_one_or_none()
    if not space:
        raise NotFoundException("Knowledge space not found")

    # Tenant admins can manage all spaces in their tenant
    if user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return space, None

    mem_q = await session.execute(
        select(KnowledgeSpaceMember).where(
            KnowledgeSpaceMember.space_id == space_id,
            KnowledgeSpaceMember.user_id == user.id,
        )
    )
    member = mem_q.scalar_one_or_none()
    if not member:
        raise ForbiddenException("Not a member of this knowledge space")

    order = {SpaceMemberRole.VIEWER: 1, SpaceMemberRole.EDITOR: 2, SpaceMemberRole.OWNER: 3}
    if order.get(SpaceMemberRole(member.role), 0) < order[min_role]:
        raise ForbiddenException("Insufficient space role")
    return space, member
