from fastapi import APIRouter, Depends, Request, Response, status

from src.modules.auth.dependencies import get_auth_service, get_current_user
from src.modules.auth.schemas import LoginInput, TokenOutput
from src.modules.auth.services import AuthService
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException

REFRESH_COOKIE = "refresh_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 dias

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=COOKIE_MAX_AGE,
    )


@auth_router.post("/login", response_model=TokenOutput)
async def login(
    body: LoginInput,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user, access_token, refresh_token = await auth_service.login(
            body.email, body.password
        )
    except ValueError:
        raise UnauthorizedException("Credenciais inválidas")

    _set_refresh_cookie(response, refresh_token)
    return TokenOutput(access_token=access_token, user_id=user.id)


@auth_router.post("/refresh", response_model=TokenOutput)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise UnauthorizedException("Refresh token ausente")

    try:
        user, new_access, new_refresh = await auth_service.refresh(token)
    except ValueError:
        raise UnauthorizedException("Refresh token inválido")

    _set_refresh_cookie(response, new_refresh)
    return TokenOutput(access_token=new_access, user_id=user.id)


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    _: User = Depends(get_current_user),
):
    response.delete_cookie(REFRESH_COOKIE)


@auth_router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }
