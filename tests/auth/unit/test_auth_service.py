import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.security import hash_password
from src.modules.auth.services import AuthService
from src.modules.users.enums.role import UserRole
from src.modules.users.models import UserModel
from src.modules.users.repository import UserRepository


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_repository):
    return AuthService(user_repository=mock_repository)


@pytest.fixture
def user():
    return UserModel(
        id=uuid.uuid4(),
        name="Ygor",
        cpf="52998224725",
        email="ygor@gmail.com",
        password=hash_password("senha123"),
        role=UserRole.COMMON,
    )


@pytest.mark.unit()
async def test_login_success(auth_service, mock_repository, user):
    mock_repository.get_by_email.return_value = user

    returned_user, access_token, refresh_token = await auth_service.login(
        user.email, "senha123"
    )

    mock_repository.get_by_email.assert_called_once_with(user.email)
    assert isinstance(returned_user, UserModel)
    assert returned_user.id == user.id
    assert access_token is not None
    assert refresh_token is not None


@pytest.mark.unit()
async def test_login_wrong_password(auth_service, mock_repository, user):
    mock_repository.get_by_email.return_value = user

    with pytest.raises(ValueError, match="Credenciais inválidas"):
        await auth_service.login(user.email, "senha_errada")

    mock_repository.get_by_email.assert_called_once_with(user.email)


@pytest.mark.unit()
async def test_login_user_not_found(auth_service, mock_repository):
    mock_repository.get_by_email.return_value = None

    with pytest.raises(ValueError, match="Credenciais inválidas"):
        await auth_service.login("naoexiste@gmail.com", "senha123")

    mock_repository.get_by_email.assert_called_once_with("naoexiste@gmail.com")


@pytest.mark.unit()
async def test_refresh_success(auth_service, mock_repository, user):
    mock_repository.get_by_id.return_value = user
    refresh_token = auth_service.create_refresh_token(str(user.id))

    returned_user, new_access, new_refresh = await auth_service.refresh(refresh_token)

    mock_repository.get_by_id.assert_called_once()
    assert isinstance(returned_user, UserModel)
    assert returned_user.id == user.id
    assert new_access is not None
    assert new_refresh is not None


@pytest.mark.unit()
async def test_refresh_user_not_found(auth_service, mock_repository, user):
    mock_repository.get_by_id.return_value = None
    refresh_token = auth_service.create_refresh_token(str(user.id))

    with pytest.raises(ValueError, match="Usuário não encontrado"):
        await auth_service.refresh(refresh_token)

    mock_repository.get_by_id.assert_called_once()


@pytest.mark.unit()
async def test_refresh_invalid_token(auth_service):
    with pytest.raises(ValueError, match="Token inválido ou expirado"):
        await auth_service.refresh("token.invalido.aqui")


@pytest.mark.unit()
async def test_refresh_with_access_token_fails(auth_service, user):
    access_token = auth_service.create_access_token(str(user.id))

    with pytest.raises(ValueError, match="Tipo de token inválido"):
        await auth_service.refresh(access_token)


@pytest.mark.unit()
def test_decode_access_token(auth_service, user):
    token = auth_service.create_access_token(str(user.id))

    user_id = auth_service.decode_token(token, expected_type="access")

    assert user_id == str(user.id)


@pytest.mark.unit()
def test_decode_refresh_token(auth_service, user):
    token = auth_service.create_refresh_token(str(user.id))

    user_id = auth_service.decode_token(token, expected_type="refresh")

    assert user_id == str(user.id)


@pytest.mark.unit()
def test_decode_token_wrong_type(auth_service, user):
    refresh_token = auth_service.create_refresh_token(str(user.id))

    with pytest.raises(ValueError, match="Tipo de token inválido"):
        auth_service.decode_token(refresh_token, expected_type="access")


@pytest.mark.unit()
def test_decode_invalid_token(auth_service):
    with pytest.raises(ValueError, match="Token inválido ou expirado"):
        auth_service.decode_token("token.invalido.aqui", expected_type="access")
