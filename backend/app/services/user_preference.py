import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_preference import UserPreferenceRepository
from app.schemas.user_preference import PreferenceResponse, PreferenceUpdate


class UserPreferenceService:
    def __init__(self, session: AsyncSession):
        self.repo = UserPreferenceRepository(session)

    async def get(self, user_id: uuid.UUID) -> PreferenceResponse:
        pref = await self.repo.get_by_user(user_id)
        if pref is None:
            pref = await self.repo.upsert(user_id, "system", "#6366f1")
        return PreferenceResponse.model_validate(pref)

    async def update(self, user_id: uuid.UUID, body: PreferenceUpdate) -> PreferenceResponse:
        pref = await self.repo.upsert(user_id, body.theme_mode, body.theme_color)
        return PreferenceResponse.model_validate(pref)
