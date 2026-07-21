import uuid

from sqlalchemy import select

from app.models.project import ProjectAsset
from app.models.video import Video
from app.repositories.base import BaseRepository


class VideoRepository(BaseRepository):
    async def get_by_id_and_tenant(self, video_id: uuid.UUID, tenant_id: uuid.UUID) -> Video | None:
        return await self._get(Video, Video.id == video_id, Video.tenant_id == tenant_id)

    def _project_filters(self, tenant_id: uuid.UUID, project_id: str | None):
        filters = [Video.tenant_id == tenant_id, Video.is_active == True]  # noqa: E712
        if project_id == "others":
            assigned_ids = select(ProjectAsset.asset_id).where(ProjectAsset.asset_type == "video")
            filters.append(Video.id.not_in(assigned_ids))
        elif project_id:
            matching_ids = select(ProjectAsset.asset_id).where(
                ProjectAsset.asset_type == "video",
                ProjectAsset.project_id == uuid.UUID(project_id),
            )
            filters.append(Video.id.in_(matching_ids))
        return filters

    async def list_by_tenant(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20,
        project_id: str | None = None,
    ) -> list[Video]:
        return await self._list(
            Video,
            *self._project_filters(tenant_id, project_id),
            order_by=Video.created_at.desc(),
            offset=offset,
            limit=limit,
        )

    async def count_by_tenant(self, tenant_id: uuid.UUID, project_id: str | None = None) -> int:
        return await self._count(Video, *self._project_filters(tenant_id, project_id))

    async def create(self, video: Video) -> Video:
        self._add(video)
        await self._flush_and_refresh(video)
        return video

    async def soft_delete(self, video: Video) -> None:
        video.is_active = False
        await self._flush_and_refresh(video)
