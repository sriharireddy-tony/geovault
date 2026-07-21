import math
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.audio import Audio
from app.models.image import Image
from app.models.project import Project, ProjectAsset
from app.models.user import User
from app.models.video import Video
from app.repositories.project import ProjectRepository
from app.schemas.audio import AudioResponse
from app.schemas.common import CreatorInfo, PaginatedResponse
from app.schemas.image import ImageResponse
from app.schemas.project import (
    MediaBucket,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectSelectionUpdate,
    ProjectUpdate,
)
from app.schemas.video import VideoResponse


def _creator(user: User) -> CreatorInfo:
    return CreatorInfo(id=user.id, name=f"{user.first_name} {user.last_name}")


def _to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        tenant_id=project.tenant_id,
        created_by=_creator(project.creator),
        title=project.title,
        is_active=project.is_active,
        created_at=project.created_at,
        assets=[
            {"id": a.id, "project_id": a.project_id, "asset_type": a.asset_type, "asset_id": a.asset_id}
            for a in project.assets
        ],
    )


def _audio_resp(a: Audio) -> AudioResponse:
    return AudioResponse(
        id=a.id, tenant_id=a.tenant_id,
        created_by=_creator(a.creator),
        title=a.title, prompt=a.prompt, file_url=a.file_url,
        project_id=a.project_id, project_ids=[],
        is_active=a.is_active, created_at=a.created_at,
    )


def _image_resp(i: Image) -> ImageResponse:
    return ImageResponse(
        id=i.id, tenant_id=i.tenant_id,
        created_by=_creator(i.creator),
        title=i.title, prompt=i.prompt, file_url=i.file_url,
        project_id=i.project_id, project_ids=[],
        is_active=i.is_active, created_at=i.created_at,
    )


def _video_resp(v: Video) -> VideoResponse:
    return VideoResponse(
        id=v.id, tenant_id=v.tenant_id,
        created_by=_creator(v.creator),
        title=v.title, prompt=v.prompt, file_url=v.file_url,
        project_id=v.project_id, project_ids=[],
        is_active=v.is_active, created_at=v.created_at,
    )


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProjectRepository(session)

    # ── helpers ─────────────────────────────────────────────────
    async def _media_via_assets(self, model, asset_type: str, project_id: uuid.UUID):
        """Fetch active media linked to a project through project_assets."""
        asset_ids_q = (
            select(ProjectAsset.asset_id)
            .where(ProjectAsset.project_id == project_id, ProjectAsset.asset_type == asset_type)
        )
        result = await self.session.execute(
            select(model)
            .where(model.id.in_(asset_ids_q), model.is_active == True)  # noqa: E712
            .order_by(model.created_at.desc())
        )
        return list(result.scalars().all())

    async def _selected_asset_ids(self, asset_type: str, project_id: uuid.UUID) -> set[uuid.UUID]:
        result = await self.session.execute(
            select(ProjectAsset.asset_id).where(
                ProjectAsset.project_id == project_id,
                ProjectAsset.asset_type == asset_type,
                ProjectAsset.is_selected == True,  # noqa: E712
            )
        )
        return set(result.scalars().all())

    # ── CRUD ────────────────────────────────────────────────────
    async def create(self, user: User, body: ProjectCreate) -> ProjectResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = Project(tenant_id=user.tenant_id, created_by=user.id, title=body.title)
        await self.repo.create(project)

        for asset_in in body.assets:
            self.repo.add_asset(ProjectAsset(
                project_id=project.id, asset_type=asset_in.asset_type, asset_id=asset_in.asset_id,
            ))

        await self.session.flush()
        await self.session.refresh(project)
        return _to_response(project)

    async def list_for_tenant(
        self, user: User, page: int = 1, size: int = 20,
    ) -> PaginatedResponse[ProjectResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        offset = (page - 1) * size
        items = await self.repo.list_by_tenant(user.tenant_id, offset=offset, limit=size)
        total = await self.repo.count_by_tenant(user.tenant_id)
        return PaginatedResponse[ProjectResponse](
            items=[_to_response(p) for p in items],
            total=total, page=page, size=size,
            pages=math.ceil(total / size) if size else 0,
        )

    async def get(self, user: User, project_id: uuid.UUID) -> ProjectResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = await self.repo.get_by_id_and_tenant(project_id, user.tenant_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")
        return _to_response(project)

    async def get_detail(self, user: User, project_id: uuid.UUID) -> ProjectDetailResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = await self.repo.get_by_id_and_tenant(project_id, user.tenant_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")

        avail_audios = await self._media_via_assets(Audio, "audio", project_id)
        avail_images = await self._media_via_assets(Image, "image", project_id)
        avail_videos = await self._media_via_assets(Video, "video", project_id)

        sel_audio_ids = await self._selected_asset_ids("audio", project_id)
        sel_image_ids = await self._selected_asset_ids("image", project_id)
        sel_video_ids = await self._selected_asset_ids("video", project_id)

        return ProjectDetailResponse(
            id=project.id,
            tenant_id=project.tenant_id,
            created_by=_creator(project.creator),
            title=project.title,
            is_active=project.is_active,
            created_at=project.created_at,
            assets=[
                {"id": a.id, "project_id": a.project_id, "asset_type": a.asset_type, "asset_id": a.asset_id}
                for a in project.assets
            ],
            available_media=MediaBucket(
                audios=[_audio_resp(a) for a in avail_audios],
                images=[_image_resp(i) for i in avail_images],
                videos=[_video_resp(v) for v in avail_videos],
            ),
            selected_media=MediaBucket(
                audios=[_audio_resp(a) for a in avail_audios if a.id in sel_audio_ids],
                images=[_image_resp(i) for i in avail_images if i.id in sel_image_ids],
                videos=[_video_resp(v) for v in avail_videos if v.id in sel_video_ids],
            ),
        )

    async def update(
        self, user: User, project_id: uuid.UUID, body: ProjectUpdate,
    ) -> ProjectResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = await self.repo.get_by_id_and_tenant(project_id, user.tenant_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")

        if body.title is not None:
            project.title = body.title

        if body.assets is not None:
            await self.repo.clear_assets(project.id)
            for asset_in in body.assets:
                self.repo.add_asset(ProjectAsset(
                    project_id=project.id, asset_type=asset_in.asset_type, asset_id=asset_in.asset_id,
                ))

        await self.session.flush()
        await self.session.refresh(project)
        return _to_response(project)

    async def update_selection(
        self, user: User, project_id: uuid.UUID, body: ProjectSelectionUpdate,
    ) -> ProjectDetailResponse:
        """Toggle is_selected on existing project_assets rows."""
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = await self.repo.get_by_id_and_tenant(project_id, user.tenant_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")

        wanted = {
            "audio": set(body.audio_ids),
            "image": set(body.image_ids),
            "video": set(body.video_ids),
        }

        for asset_type, ids in wanted.items():
            assigned_q = await self.session.execute(
                select(ProjectAsset.asset_id).where(
                    ProjectAsset.project_id == project_id,
                    ProjectAsset.asset_type == asset_type,
                )
            )
            assigned_ids = set(assigned_q.scalars().all())
            invalid = ids - assigned_ids
            if invalid:
                raise ForbiddenException(
                    f"{asset_type.title()} {invalid} not assigned to this project"
                )

            # mark selected
            if ids:
                await self.session.execute(
                    update(ProjectAsset)
                    .where(
                        ProjectAsset.project_id == project_id,
                        ProjectAsset.asset_type == asset_type,
                        ProjectAsset.asset_id.in_(ids),
                    )
                    .values(is_selected=True)
                )
            # unmark the rest
            not_selected = assigned_ids - ids
            if not_selected:
                await self.session.execute(
                    update(ProjectAsset)
                    .where(
                        ProjectAsset.project_id == project_id,
                        ProjectAsset.asset_type == asset_type,
                        ProjectAsset.asset_id.in_(not_selected),
                    )
                    .values(is_selected=False)
                )

        await self.session.flush()
        await self.session.refresh(project)
        return await self.get_detail(user, project_id)

    async def delete(self, user: User, project_id: uuid.UUID) -> None:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        project = await self.repo.get_by_id_and_tenant(project_id, user.tenant_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")
        await self.repo.soft_delete(project)
