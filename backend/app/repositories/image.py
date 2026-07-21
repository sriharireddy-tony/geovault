import uuid

from sqlalchemy import select

from app.models.image import Image
from app.models.project import ProjectAsset
from app.repositories.base import BaseRepository


class ImageRepository(BaseRepository):
    async def get_by_id_and_tenant(self, image_id: uuid.UUID, tenant_id: uuid.UUID) -> Image | None:
        return await self._get(Image, Image.id == image_id, Image.tenant_id == tenant_id)

    def _project_filters(self, tenant_id: uuid.UUID, project_id: str | None):
        filters = [Image.tenant_id == tenant_id, Image.is_active == True]  # noqa: E712
        if project_id == "others":
            assigned_ids = select(ProjectAsset.asset_id).where(ProjectAsset.asset_type == "image")
            filters.append(Image.id.not_in(assigned_ids))
        elif project_id:
            matching_ids = select(ProjectAsset.asset_id).where(
                ProjectAsset.asset_type == "image",
                ProjectAsset.project_id == uuid.UUID(project_id),
            )
            filters.append(Image.id.in_(matching_ids))
        return filters

    async def list_by_tenant(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20,
        project_id: str | None = None,
    ) -> list[Image]:
        return await self._list(
            Image,
            *self._project_filters(tenant_id, project_id),
            order_by=Image.created_at.desc(),
            offset=offset,
            limit=limit,
        )

    async def count_by_tenant(self, tenant_id: uuid.UUID, project_id: str | None = None) -> int:
        return await self._count(Image, *self._project_filters(tenant_id, project_id))

    async def create(self, image: Image) -> Image:
        self._add(image)
        await self._flush_and_refresh(image)
        return image

    async def soft_delete(self, image: Image) -> None:
        image.is_active = False
        await self._flush_and_refresh(image)
