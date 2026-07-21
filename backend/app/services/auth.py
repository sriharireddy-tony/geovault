from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.user_preference import UserPreference
from app.repositories.tenant import TenantRepository
from app.repositories.user import UserRepository
from app.schemas.auth import SignupRequest, Token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.tenant_repo = TenantRepository(session)
        self.session = session

    async def signup(self, body: SignupRequest) -> Token:
        existing = await self.user_repo.get_by_email(body.email)
        if existing:
            raise ConflictException("Email already registered")

        tenant = Tenant(name=body.tenant_name)
        await self.tenant_repo.create(tenant)

        user = User(
            tenant_id=tenant.id,
            email=body.email,
            password_hash=hash_password(body.password),
            first_name=body.first_name,
            last_name=body.last_name,
            role=UserRole.ADMIN,
        )
        await self.user_repo.create(user)

        pref = UserPreference(user_id=user.id)
        self.session.add(pref)
        await self.session.flush()

        return Token(
            access_token=create_access_token(user.id, tenant.id, user.role.value),
        )

    async def login(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            raise UnauthorizedException("Incorrect email or password")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Incorrect email or password")

        return Token(
            access_token=create_access_token(user.id, user.tenant_id, user.role.value),
        )
