import uuid

from app.models.project import Project, ProjectAsset
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    async def get_by_id_and_tenant(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Project | None:
        return await self._get(Project, Project.id == project_id, Project.tenant_id == tenant_id)

    async def list_by_tenant(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20,
    ) -> list[Project]:
        return await self._list(
            Project,
            Project.tenant_id == tenant_id,
            Project.is_active == True,  # noqa: E712
            order_by=Project.created_at.desc(),
            offset=offset,
            limit=limit,
        )

    async def count_by_tenant(self, tenant_id: uuid.UUID) -> int:
        return await self._count(
            Project, Project.tenant_id == tenant_id, Project.is_active == True,  # noqa: E712
        )

    async def create(self, project: Project) -> Project:
        self._add(project)
        await self._flush_and_refresh(project)
        return project

    def add_asset(self, asset: ProjectAsset) -> None:
        self._add(asset)

    async def clear_assets(self, project_id: uuid.UUID) -> None:
        from sqlalchemy import delete
        await self.session.execute(
            delete(ProjectAsset).where(ProjectAsset.project_id == project_id)
        )

    async def soft_delete(self, project: Project) -> None:
        project.is_active = False
        await self._flush_and_refresh(project)
