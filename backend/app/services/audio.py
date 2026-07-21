import logging
import math
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tts import text_to_speech
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.audio import Audio
from app.models.project import ProjectAsset
from app.models.user import User
from app.repositories.audio import AudioRepository
from app.schemas.audio import AudioCreate, AudioResponse, AudioUpdate
from app.schemas.common import CreatorInfo, PaginatedResponse
from app.utils.storage import save_audio_file

logger = logging.getLogger(__name__)


async def _sync_project_assets(
    session: AsyncSession, asset_id: uuid.UUID, asset_type: str, wanted_pids: set[uuid.UUID],
) -> None:
    """Add/remove project_assets rows while preserving is_selected on kept rows."""
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


async def _get_project_ids(session: AsyncSession, asset_id: uuid.UUID, asset_type: str = "audio") -> list[uuid.UUID]:
    result = await session.execute(
        select(ProjectAsset.project_id).where(
            ProjectAsset.asset_id == asset_id,
            ProjectAsset.asset_type == asset_type,
        )
    )
    return list(result.scalars().all())


def _to_response(audio: Audio, project_ids: list[uuid.UUID] | None = None) -> AudioResponse:
    creator = audio.creator
    return AudioResponse(
        id=audio.id,
        tenant_id=audio.tenant_id,
        created_by=CreatorInfo(id=creator.id, name=f"{creator.first_name} {creator.last_name}"),
        title=audio.title,
        prompt=audio.prompt,
        file_url=audio.file_url,
        project_id=audio.project_id,
        project_ids=project_ids or [],
        is_active=audio.is_active,
        created_at=audio.created_at,
    )


class AudioService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AudioRepository(session)

    async def create(self, user: User, body: AudioCreate) -> AudioResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")

        file_url = None
        if body.prompt:
            try:
                audio_bytes = await text_to_speech(
                    text=body.prompt,
                    language=body.language,
                    speaker=body.speaker,
                )
                file_url = save_audio_file(audio_bytes)
                logger.info("Audio generated: %s", file_url)
            except Exception:
                logger.exception("TTS generation failed, saving without audio")

        audio = Audio(
            tenant_id=user.tenant_id,
            created_by=user.id,
            project_id=body.project_id,
            title=body.title,
            prompt=body.prompt,
            file_url=file_url,
        )
        await self.repo.create(audio)
        if body.project_id:
            self.session.add(ProjectAsset(
                project_id=body.project_id, asset_type="audio", asset_id=audio.id,
            ))
            await self.session.flush()
        pids = await _get_project_ids(self.session, audio.id, "audio")
        return _to_response(audio, pids)

    async def list_for_tenant(
        self, user: User, page: int = 1, size: int = 20,
        project_id: str | None = None,
    ) -> PaginatedResponse[AudioResponse]:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        offset = (page - 1) * size
        items = await self.repo.list_by_tenant(user.tenant_id, offset=offset, limit=size, project_id=project_id)
        total = await self.repo.count_by_tenant(user.tenant_id, project_id=project_id)
        responses = []
        for a in items:
            pids = await _get_project_ids(self.session, a.id, "audio")
            responses.append(_to_response(a, pids))
        return PaginatedResponse[AudioResponse](
            items=responses,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size else 0,
        )

    async def update(self, user: User, audio_id: uuid.UUID, body: AudioUpdate) -> AudioResponse:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        audio = await self.repo.get_by_id_and_tenant(audio_id, user.tenant_id)
        if not audio or not audio.is_active:
            raise NotFoundException("Audio not found")

        await _sync_project_assets(self.session, audio_id, "audio", set(body.project_ids))

        pids = await _get_project_ids(self.session, audio_id, "audio")
        return _to_response(audio, pids)

    async def delete(self, user: User, audio_id: uuid.UUID) -> None:
        if not user.tenant_id:
            raise ForbiddenException("No tenant context")
        audio = await self.repo.get_by_id_and_tenant(audio_id, user.tenant_id)
        if not audio or not audio.is_active:
            raise NotFoundException("Audio not found")
        await self.repo.soft_delete(audio)
