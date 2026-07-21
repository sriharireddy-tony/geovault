import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get(self, model: Any, *filters: Any) -> Any | None:
        result = await self.session.execute(select(model).where(*filters))
        return result.scalar_one_or_none()

    async def _list(
        self,
        model: Any,
        *filters: Any,
        order_by: Any = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Any]:
        stmt = select(model).where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _count(self, model: Any, *filters: Any) -> int:
        stmt = select(func.count()).select_from(model).where(*filters)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    def _add(self, entity: Any) -> None:
        self.session.add(entity)

    async def _flush_and_refresh(self, entity: Any) -> None:
        await self.session.flush()
        await self.session.refresh(entity)
