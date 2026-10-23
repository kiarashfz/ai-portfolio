from sqlalchemy.ext.asyncio import AsyncSession

from db.base_stage_repository import BaseSingleStageRepository
from db.base_stage_services import BaseSingleStageService
from db.models import User
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID


class UserService(BaseSingleStageService[User]):
    def __init__(self, jwt_public_key: str, jwt_private_key: str, user_repo: BaseSingleStageRepository = None):
        self.jwt_public_key = jwt_public_key
        self.jwt_private_key = jwt_private_key
        self.user_repo = user_repo or BaseSingleStageRepository(User)
        super().__init__(self.user_repo, User)

    async def signup(self, session: AsyncSession, username: str, password: str) -> User:
        existing = await self.get_by_username(session=session, username=username)
        if existing:
            raise ValueError(f"Username '{username}' is already taken")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_user = await self.user_repo.create(
            session=session,
            username=username,
            password_hash=password_hash,
        )
        await session.commit()
        return new_user

    async def login(self, session, username: str, password: str) -> dict:
        user = await self.get_by_username(session=session, username=username)
        if not user:
            raise ValueError("Invalid username or password")

        if not await self.verify_password(plain=password, hashed=user.password_hash):
            raise ValueError("Invalid username or password")

        access_token = self._issue_token(user_id=user.id, expires_in_minutes=60)
        refresh_token = self._issue_token(user_id=user.id, expires_in_minutes=60 * 24 * 30)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    async def get_by_username(self, session, username: str) -> User | None:
        users, _ = await self.find(
            session=session,
            filters={"username": {"match_mode": "equals", "value": username}},
        )
        return users[0] if users else None

    async def get_by_id(self, session, user_id: UUID) -> User | None:
        users, _ = await self.find(
            session=session,
            filters={"id": {"match_mode": "equals", "value": user_id}},
        )
        return users[0] if users else None

    def decode_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.jwt_public_key,
            algorithms=["RS256"],
        )

    def _issue_token(self, user_id: UUID, expires_in_minutes: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=expires_in_minutes),
        }
        return jwt.encode(payload, self.jwt_private_key, algorithm="RS256")