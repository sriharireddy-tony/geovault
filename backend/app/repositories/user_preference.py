import uuid

from app.models.user_preference import UserPreference
from app.repositories.base import BaseRepository


class UserPreferenceRepository(BaseRepository):
    async def get_by_user(self, user_id: uuid.UUID) -> UserPreference | None:
        return await self._get(UserPreference, UserPreference.user_id == user_id)

    async def upsert(self, user_id: uuid.UUID, theme_mode: str, theme_color: str) -> UserPreference:
        pref = await self.get_by_user(user_id)
        if pref is None:
            pref = UserPreference(user_id=user_id, theme_mode=theme_mode, theme_color=theme_color)
            self._add(pref)
        else:
            pref.theme_mode = theme_mode
            pref.theme_color = theme_color
        await self._flush_and_refresh(pref)
        return pref
