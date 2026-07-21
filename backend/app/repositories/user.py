import uuid

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._get(User, User.id == user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self._get(User, User.email == email)

    async def list_by_tenant(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20,
    ) -> list[User]:
        return await self._list(
            User,
            User.tenant_id == tenant_id,
            User.is_active == True,  # noqa: E712
            order_by=User.created_at.desc(),
            offset=offset,
            limit=limit,
        )

    async def count_by_tenant(self, tenant_id: uuid.UUID) -> int:
        return await self._count(
            User, User.tenant_id == tenant_id, User.is_active == True,  # noqa: E712
        )

    async def create(self, user: User) -> User:
        self._add(user)
        await self._flush_and_refresh(user)
        return user

    async def deactivate(self, user: User) -> User:
        user.is_active = False
        await self._flush_and_refresh(user)
        return user
