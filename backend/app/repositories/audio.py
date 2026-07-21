import uuid

from sqlalchemy import select

from app.models.audio import Audio
from app.models.project import ProjectAsset
from app.repositories.base import BaseRepository


class AudioRepository(BaseRepository):
    async def get_by_id_and_tenant(self, audio_id: uuid.UUID, tenant_id: uuid.UUID) -> Audio | None:
        return await self._get(Audio, Audio.id == audio_id, Audio.tenant_id == tenant_id)

    def _project_filters(self, tenant_id: uuid.UUID, project_id: str | None):
        filters = [Audio.tenant_id == tenant_id, Audio.is_active == True]  # noqa: E712
        if project_id == "others":
            assigned_ids = select(ProjectAsset.asset_id).where(ProjectAsset.asset_type == "audio")
            filters.append(Audio.id.not_in(assigned_ids))
        elif project_id:
            matching_ids = select(ProjectAsset.asset_id).where(
                ProjectAsset.asset_type == "audio",
                ProjectAsset.project_id == uuid.UUID(project_id),
            )
            filters.append(Audio.id.in_(matching_ids))
        return filters

    async def list_by_tenant(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20,
        project_id: str | None = None,
    ) -> list[Audio]:
        return await self._list(
            Audio,
            *self._project_filters(tenant_id, project_id),
            order_by=Audio.created_at.desc(),
            offset=offset,
            limit=limit,
        )

    async def count_by_tenant(self, tenant_id: uuid.UUID, project_id: str | None = None) -> int:
        return await self._count(Audio, *self._project_filters(tenant_id, project_id))

    async def create(self, audio: Audio) -> Audio:
        self._add(audio)
        await self._flush_and_refresh(audio)
        return audio

    async def soft_delete(self, audio: Audio) -> None:
        audio.is_active = False
        await self._flush_and_refresh(audio)
