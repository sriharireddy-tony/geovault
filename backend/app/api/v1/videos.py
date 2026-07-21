import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, UploadFile

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import BadRequestException
from app.models.project import ProjectAsset
from app.models.video import Video
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.video import VideoCreate, VideoResponse, VideoUpdate
from app.services.video import VideoService, _get_project_ids, _to_response
from app.utils.pagination import PaginationParams
from app.utils.storage import ALLOWED_VIDEO, save_uploaded_video

router = APIRouter()


@router.post("", response_model=VideoResponse, status_code=201)
async def create_video(
    body: VideoCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> VideoResponse:
    svc = VideoService(session)
    return await svc.create(current_user, body)


@router.post("/import", response_model=list[VideoResponse], status_code=201)
async def import_videos(
    files: list[UploadFile],
    session: DBSession,
    current_user: CurrentUser,
    project_id: uuid.UUID = Form(...),
):
    if not current_user.tenant_id:
        raise BadRequestException("No tenant context")
    results: list[VideoResponse] = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_VIDEO:
            raise BadRequestException(f"Invalid video file type: {f.filename}")
        data = await f.read()
        url = save_uploaded_video(data, f.filename or "video.mp4")
        title = Path(f.filename or "video").stem
        video = Video(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            project_id=project_id,
            title=title,
            file_url=url,
        )
        session.add(video)
        await session.flush()
        await session.refresh(video)
        session.add(ProjectAsset(project_id=project_id, asset_type="video", asset_id=video.id))
        await session.flush()
        pids = await _get_project_ids(session, video.id, "video")
        results.append(_to_response(video, pids))
    return results


@router.get("", response_model=PaginatedResponse[VideoResponse])
async def list_videos(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    project_id: str | None = Query(default=None),
) -> PaginatedResponse[VideoResponse]:
    svc = VideoService(session)
    return await svc.list_for_tenant(current_user, pagination.page, pagination.size, project_id=project_id)


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: uuid.UUID,
    body: VideoUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> VideoResponse:
    svc = VideoService(session)
    return await svc.update(current_user, video_id, body)


@router.delete("/{video_id}", response_model=MessageResponse)
async def delete_video(
    video_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    svc = VideoService(session)
    await svc.delete(current_user, video_id)
    return MessageResponse(detail="Video deleted")
