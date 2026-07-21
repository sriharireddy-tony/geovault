import re
import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DBSession
from app.core.config import get_settings
from app.core.exceptions import NotFoundException
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectSelectionUpdate,
    ProjectUpdate,
)
from app.services.project import ProjectService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    svc = ProjectService(session)
    return await svc.create(current_user, body)


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[ProjectResponse]:
    svc = ProjectService(session)
    return await svc.list_for_tenant(current_user, pagination.page, pagination.size)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> ProjectDetailResponse:
    svc = ProjectService(session)
    return await svc.get_detail(current_user, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    svc = ProjectService(session)
    return await svc.update(current_user, project_id, body)


@router.put("/{project_id}/selection", response_model=ProjectDetailResponse)
async def update_project_selection(
    project_id: uuid.UUID,
    body: ProjectSelectionUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> ProjectDetailResponse:
    svc = ProjectService(session)
    return await svc.update_selection(current_user, project_id, body)


@router.post("/{project_id}/export", response_model=MessageResponse)
async def export_project(
    project_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    """Copy only selected project media to the local export directory."""
    svc = ProjectService(session)
    detail = await svc.get_detail(current_user, project_id)

    settings = get_settings()
    safe_title = re.sub(r'[<>:"/\\|?*]', "_", detail.title).strip() or "Untitled"
    project_dir = Path(settings.PROJECT_EXPORT_DIR) / safe_title

    media_root = Path("media")
    copied = 0

    buckets = {
        "audios": detail.selected_media.audios,
        "images": detail.selected_media.images,
        "videos": detail.selected_media.videos,
    }

    for folder_name, items in buckets.items():
        if not items:
            continue
        dest_folder = project_dir / folder_name
        dest_folder.mkdir(parents=True, exist_ok=True)
        for item in items:
            if not item.file_url:
                continue
            rel_path = item.file_url.lstrip("/")
            src = media_root.parent / rel_path
            if not src.is_file():
                continue
            dest = dest_folder / src.name
            shutil.copy2(str(src), str(dest))
            copied += 1

    if copied == 0:
        raise NotFoundException("No media files found to export")

    return MessageResponse(detail=f"Exported {copied} file(s) to {project_dir}")


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    svc = ProjectService(session)
    await svc.delete(current_user, project_id)
    return MessageResponse(detail="Project deleted")
