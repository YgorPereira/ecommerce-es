import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.services import AuthService
from src.modules.users.models import UserModel
from src.modules.users.repository import UserRepository

bearer_scheme = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserModel:
    try:
        user_id = auth_service.decode_token(credentials.credentials, expected_type="access")
        user = auth_service.user_repository.get_by_id(uuid.UUID(user_id))
        if not user:
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user