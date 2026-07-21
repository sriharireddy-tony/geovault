from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import SignupRequest, Token
from app.schemas.user import ProfileUpdate, UserResponse
from app.services.auth import AuthService
from app.services.profile import ProfileService

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=201)
async def signup(body: SignupRequest, session: DBSession) -> Token:
    svc = AuthService(session)
    return await svc.signup(body)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DBSession,
) -> Token:
    svc = AuthService(session)
    return await svc.login(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    body: ProfileUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    svc = ProfileService(session)
    return await svc.update_profile(current_user, body)
