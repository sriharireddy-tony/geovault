import uuid

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository):
    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        return await self._get(Tenant, Tenant.id == tenant_id)

    async def create(self, tenant: Tenant) -> Tenant:
        self._add(tenant)
        await self._flush_and_refresh(tenant)
        return tenant
