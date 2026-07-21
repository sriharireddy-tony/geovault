import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.user_preference import UserPreference
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    async def list_users(
        self, current_user: User, page: int = 1, size: int = 20,
    ) -> PaginatedResponse[UserResponse]:
        if current_user.role == UserRole.SUPER_ADMIN:
            raise ForbiddenException("Use tenant-scoped endpoints")
        tenant_id = current_user.tenant_id
        if not tenant_id:
            raise ForbiddenException("No tenant context")

        offset = (page - 1) * size
        items = await self.repo.list_by_tenant(tenant_id, offset=offset, limit=size)
        total = await self.repo.count_by_tenant(tenant_id)
        return PaginatedResponse[UserResponse](
            items=[UserResponse.model_validate(u) for u in items],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size else 0,
        )

    async def create_user(
        self, current_user: User, body: UserCreate,
    ) -> UserResponse:
        if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
            raise ForbiddenException("Only admins can create users")
        if not current_user.tenant_id:
            raise ForbiddenException("No tenant context")

        existing = await self.repo.get_by_email(body.email)
        if existing:
            raise ConflictException("Email already registered")

        if body.role == UserRole.SUPER_ADMIN:
            raise ForbiddenException("Cannot create SUPER_ADMIN")
        if body.role == UserRole.ADMIN and current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenException("Only SUPER_ADMIN can create admins")

        user = User(
            tenant_id=current_user.tenant_id,
            email=body.email,
            password_hash=hash_password(body.password),
            first_name=body.first_name,
            last_name=body.last_name,
            role=body.role,
            created_by=current_user.id,
        )
        await self.repo.create(user)

        pref = UserPreference(user_id=user.id)
        self.session.add(pref)
        await self.session.flush()

        return UserResponse.model_validate(user)

    async def deactivate_user(
        self, current_user: User, target_id: uuid.UUID,
    ) -> UserResponse:
        if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
            raise ForbiddenException("Only admins can deactivate users")

        target = await self.repo.get_by_id(target_id)
        if not target:
            raise NotFoundException("User not found")
        if current_user.tenant_id and target.tenant_id != current_user.tenant_id:
            raise ForbiddenException("Cannot deactivate users outside your tenant")
        if target.id == current_user.id:
            raise ForbiddenException("Cannot deactivate yourself")

        await self.repo.deactivate(target)
        return UserResponse.model_validate(target)
