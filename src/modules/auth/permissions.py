from fastapi import Depends

from src.modules.auth.dependencies import get_current_user
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin():
        raise UnauthorizedException("Acesso restrito a administradores")
    return current_user
