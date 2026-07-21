from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import ProfileUpdate, UserResponse


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def update_profile(self, user: User, body: ProfileUpdate) -> UserResponse:
        if body.first_name is not None:
            user.first_name = body.first_name
        if body.last_name is not None:
            user.last_name = body.last_name
        if body.password is not None:
            user.password_hash = hash_password(body.password)

        await self.repo.session.flush()
        await self.repo.session.refresh(user)
        return UserResponse.model_validate(user)
