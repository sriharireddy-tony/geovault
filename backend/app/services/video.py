import math
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.project import ProjectAsset
from app.models.user import User
from app.models.video import Video
from app.repositories.video import VideoRepository
from app.schemas.common import CreatorInfo, PaginatedResponse
from app.schemas.video import VideoCreate, VideoResponse, VideoUpdate


async def _sync_project_assets(
    session: AsyncSession, asset_id: uuid.UUID, asset_type: str, wanted_pids: set[uuid.UUID],
) -> None:
    existing = await session.execute(
        select(ProjectAsset).where(
            ProjectAsset.asset_id == asset_id,
            ProjectAsset.asset_type == asset_type,
        )
    )
    existing_map = {pa.project_id: pa for pa in existing.scalars().all()}
    current_pids = set(existing_map.keys())

    to_remove = current_pids - wanted_pids
    to_add = wanted_pids - current_pids

    if to_remove:
        await session.execute(
            delete(ProjectAsset).where(
                ProjectAsset.asset_id == asset_id,
                ProjectAsset.asset_type == asset_type,
                ProjectAsset.project_id.in_(to_remove),
            )
        )
    for pid in to_add:
        session.add(ProjectAsset(project_id=pid, asset_type=asset_type, asset_id=asset_id))
    await session.flush()


async def _get_project_ids(session: AsyncSession, asset_id: uuid.UUID, asset_type: str = "video") -> list[uuid.UUID]:
    result = await session.execute(
        select(ProjectAsset.project_id).where(
            ProjectAsset.asset_id == asset_id,
            ProjectAsset.asset_type == asset_type,
        )
    )
    return list(result.scalars().all())


def _to_response(video: Video, project_ids: list[uuid.UUID] | None = None) -> VideoResponse:
    creator = video.creator
    return VideoResponse(
        id=video.id,
        tenant_id=video.tenant_id,
        created_by=CreatorInfo(id=creator.id, name=f"{creator.first_name} {creator.last_name}"),
        title=video.title,
        prompt=video.prompt,
        file_url=video.file_url,
        project_id=video.project_id,
        project_ids=project_ids or [],
        is_active=video.is_active,
        created_at=video.created_at,
    )


class VideoService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = VideoRepository(session)

    async def create(self, user: User, body: VideoCreate) -> VideoResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        video = Video(
            tenant_id=user.tenant_id,
            created_by=user.id,
            project_id=body.project_id,
            title=body.title,
            prompt=body.prompt,
        )
        await self.repo.create(video)
        if body.project_id:
            self.session.add(ProjectAsset(
                project_id=body.project_id, asset_type="video", asset_id=video.id,
            ))
            await self.session.flush()
        pids = await _get_project_ids(self.session, video.id)
        return _to_response(video, pids)

    async def list_for_tenant(
        self, user: User, page: int = 1, size: int = 20,
        project_id: str | None = None,
    ) -> PaginatedResponse[VideoResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        offset = (page - 1) * size
        items = await self.repo.list_by_tenant(user.tenant_id, offset=offset, limit=size, project_id=project_id)
        total = await self.repo.count_by_tenant(user.tenant_id, project_id=project_id)
        responses = []
        for v in items:
            pids = await _get_project_ids(self.session, v.id)
            responses.append(_to_response(v, pids))
        return PaginatedResponse[VideoResponse](
            items=responses,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size else 0,
        )

    async def update(self, user: User, video_id: uuid.UUID, body: VideoUpdate) -> VideoResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        video = await self.repo.get_by_id_and_tenant(video_id, user.tenant_id)
        if not video or not video.is_active:
            raise NotFoundException("Video not found")

        await _sync_project_assets(self.session, video_id, "video", set(body.project_ids))

        pids = await _get_project_ids(self.session, video_id)
        return _to_response(video, pids)

    async def delete(self, user: User, video_id: uuid.UUID) -> None:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        video = await self.repo.get_by_id_and_tenant(video_id, user.tenant_id)
        if not video or not video.is_active:
            raise NotFoundException("Video not found")
        await self.repo.soft_delete(video)
