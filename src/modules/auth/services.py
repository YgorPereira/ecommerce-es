import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from src.core.security import verify_password
from src.core.settings import settings
from src.modules.users.models import UserModel
from src.modules.users.repository import UserRepository

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _create_token(
        self, user_id: str, token_type: str, expires_delta: timedelta
    ) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        return jwt.encode(
            {"sub": user_id, "exp": expire, "type": token_type},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def create_access_token(self, user_id: str) -> str:
        return self._create_token(
            user_id, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    def create_refresh_token(self, user_id: str) -> str:
        return self._create_token(
            user_id, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

    def decode_token(self, token: str, expected_type: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != expected_type:
                raise ValueError("Tipo de token inválido")
            return payload["sub"]
        except InvalidTokenError:
            raise ValueError("Token inválido ou expirado")

    async def login(self, email: str, password: str) -> tuple[UserModel, str, str]:
        user = await self.user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise ValueError("Credenciais inválidas")

        access_token = self.create_access_token(str(user.id))
        refresh_token = self.create_refresh_token(str(user.id))
        return user, access_token, refresh_token

    async def refresh(self, refresh_token: str) -> tuple[UserModel, str, str]:
        user_id = self.decode_token(refresh_token, expected_type="refresh")
        user = await self.user_repository.get_by_id(uuid.UUID(user_id))

        if not user:
            raise ValueError("Usuário não encontrado")

        new_access = self.create_access_token(str(user.id))
        new_refresh = self.create_refresh_token(str(user.id))
        return user, new_access, new_refresh
