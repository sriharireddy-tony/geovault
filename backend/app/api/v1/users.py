import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[UserResponse]:
    svc = UserService(session)
    return await svc.list_users(current_user, pagination.page, pagination.size)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    body: UserCreate,
    session: DBSession,
    current_user: AdminUser,
) -> UserResponse:
    svc = UserService(session)
    return await svc.create_user(current_user, body)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    session: DBSession,
    current_user: AdminUser,
) -> UserResponse:
    svc = UserService(session)
    return await svc.deactivate_user(current_user, user_id)
