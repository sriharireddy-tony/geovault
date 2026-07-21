import math
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.image import Image
from app.models.project import ProjectAsset
from app.models.user import User
from app.repositories.image import ImageRepository
from app.schemas.common import CreatorInfo, PaginatedResponse
from app.schemas.image import ImageCreate, ImageResponse, ImageUpdate


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


async def _get_project_ids(session: AsyncSession, asset_id: uuid.UUID, asset_type: str = "image") -> list[uuid.UUID]:
    result = await session.execute(
        select(ProjectAsset.project_id).where(
            ProjectAsset.asset_id == asset_id,
            ProjectAsset.asset_type == asset_type,
        )
    )
    return list(result.scalars().all())


def _to_response(image: Image, project_ids: list[uuid.UUID] | None = None) -> ImageResponse:
    creator = image.creator
    return ImageResponse(
        id=image.id,
        tenant_id=image.tenant_id,
        created_by=CreatorInfo(id=creator.id, name=f"{creator.first_name} {creator.last_name}"),
        title=image.title,
        prompt=image.prompt,
        file_url=image.file_url,
        project_id=image.project_id,
        project_ids=project_ids or [],
        is_active=image.is_active,
        created_at=image.created_at,
    )


class ImageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ImageRepository(session)

    async def create(self, user: User, body: ImageCreate) -> ImageResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        image = Image(
            tenant_id=user.tenant_id,
            created_by=user.id,
            project_id=body.project_id,
            title=body.title,
            prompt=body.prompt,
        )
        await self.repo.create(image)
        if body.project_id:
            self.session.add(ProjectAsset(
                project_id=body.project_id, asset_type="image", asset_id=image.id,
            ))
            await self.session.flush()
        pids = await _get_project_ids(self.session, image.id)
        return _to_response(image, pids)

    async def list_for_tenant(
        self, user: User, page: int = 1, size: int = 20,
        project_id: str | None = None,
    ) -> PaginatedResponse[ImageResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        offset = (page - 1) * size
        items = await self.repo.list_by_tenant(user.tenant_id, offset=offset, limit=size, project_id=project_id)
        total = await self.repo.count_by_tenant(user.tenant_id, project_id=project_id)
        responses = []
        for i in items:
            pids = await _get_project_ids(self.session, i.id)
            responses.append(_to_response(i, pids))
        return PaginatedResponse[ImageResponse](
            items=responses,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size else 0,
        )

    async def update(self, user: User, image_id: uuid.UUID, body: ImageUpdate) -> ImageResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        image = await self.repo.get_by_id_and_tenant(image_id, user.tenant_id)
        if not image or not image.is_active:
            raise NotFoundException("Image not found")

        await _sync_project_assets(self.session, image_id, "image", set(body.project_ids))

        pids = await _get_project_ids(self.session, image_id)
        return _to_response(image, pids)

    async def delete(self, user: User, image_id: uuid.UUID) -> None:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        image = await self.repo.get_by_id_and_tenant(image_id, user.tenant_id)
        if not image or not image.is_active:
            raise NotFoundException("Image not found")
        await self.repo.soft_delete(image)
