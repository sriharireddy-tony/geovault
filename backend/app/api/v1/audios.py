import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, UploadFile

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import BadRequestException
from app.models.audio import Audio
from app.models.project import ProjectAsset
from app.schemas.audio import AudioCreate, AudioResponse, AudioUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.audio import AudioService, _get_project_ids, _to_response
from app.utils.pagination import PaginationParams
from app.utils.storage import ALLOWED_AUDIO, save_uploaded_audio

router = APIRouter()


@router.post("", response_model=AudioResponse, status_code=201)
async def create_audio(
    body: AudioCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> AudioResponse:
    svc = AudioService(session)
    return await svc.create(current_user, body)


@router.post("/import", response_model=list[AudioResponse], status_code=201)
async def import_audios(
    files: list[UploadFile],
    session: DBSession,
    current_user: CurrentUser,
    project_id: uuid.UUID = Form(...),
):
    if not current_user.tenant_id:
        raise BadRequestException("No tenant context")
    results: list[AudioResponse] = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_AUDIO:
            raise BadRequestException(f"Invalid audio file type: {f.filename}")
        data = await f.read()
        url = save_uploaded_audio(data, f.filename or "audio.wav")
        title = Path(f.filename or "audio").stem
        audio = Audio(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            project_id=project_id,
            title=title,
            file_url=url,
        )
        session.add(audio)
        await session.flush()
        await session.refresh(audio)
        session.add(ProjectAsset(project_id=project_id, asset_type="audio", asset_id=audio.id))
        await session.flush()
        pids = await _get_project_ids(session, audio.id, "audio")
        results.append(_to_response(audio, pids))
    return results


@router.get("", response_model=PaginatedResponse[AudioResponse])
async def list_audios(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    project_id: str | None = Query(default=None),
) -> PaginatedResponse[AudioResponse]:
    svc = AudioService(session)
    return await svc.list_for_tenant(current_user, pagination.page, pagination.size, project_id=project_id)


@router.put("/{audio_id}", response_model=AudioResponse)
async def update_audio(
    audio_id: uuid.UUID,
    body: AudioUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> AudioResponse:
    svc = AudioService(session)
    return await svc.update(current_user, audio_id, body)


@router.delete("/{audio_id}", response_model=MessageResponse)
async def delete_audio(
    audio_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    svc = AudioService(session)
    await svc.delete(current_user, audio_id)
    return MessageResponse(detail="Audio deleted")
