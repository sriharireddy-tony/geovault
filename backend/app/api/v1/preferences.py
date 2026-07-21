from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.schemas.user_preference import PreferenceResponse, PreferenceUpdate
from app.services.user_preference import UserPreferenceService

router = APIRouter()


@router.get("", response_model=PreferenceResponse)
async def get_preferences(
    session: DBSession,
    current_user: CurrentUser,
) -> PreferenceResponse:
    svc = UserPreferenceService(session)
    return await svc.get(current_user.id)


@router.put("", response_model=PreferenceResponse)
async def update_preferences(
    body: PreferenceUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> PreferenceResponse:
    svc = UserPreferenceService(session)
    return await svc.update(current_user.id, body)
