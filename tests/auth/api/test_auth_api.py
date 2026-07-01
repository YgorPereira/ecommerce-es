import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.auth.dependencies import get_auth_service, get_current_user
from src.modules.auth.services import AuthService
from src.modules.users.entity import User
from src.modules.users.enums.role import UserRole


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_auth_service():
    service = AsyncMock(spec=AuthService)
    app.dependency_overrides[get_auth_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def user():
    return User(
        id=uuid.uuid4(),
        name="Ygor Pereira",
        cpf="52998224725",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )


@pytest.fixture
def authenticated_client(client, user):
    app.dependency_overrides[get_current_user] = lambda: user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.api
def test_login_success(client, mock_auth_service, user):
    mock_auth_service.login.return_value = (
        user,
        "access_token_fake",
        "refresh_token_fake",
    )

    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "senha1234"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["access_token"] == "access_token_fake"
    assert body["user_id"] == str(user.id)
    assert body["token_type"] == "bearer"
    assert "refresh_token" in response.cookies

    mock_auth_service.login.assert_awaited_once_with(user.email, "senha1234")


@pytest.mark.api
def test_login_invalid_credentials(client, mock_auth_service):
    mock_auth_service.login.side_effect = ValueError("Credenciais inválidas")

    response = client.post(
        "/auth/login",
        json={"email": "errado@gmail.com", "password": "senha_errada"},
    )

    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Credenciais inválidas"


@pytest.mark.api
def test_login_missing_fields(client, mock_auth_service):
    response = client.post("/auth/login", json={"email": "ygor@gmail.com"})

    assert response.status_code == 422


@pytest.mark.api
def test_refresh_success(client, mock_auth_service, user):
    mock_auth_service.refresh.return_value = (
        user,
        "new_access_token",
        "new_refresh_token",
    )

    client.cookies.set("refresh_token", "valid_refresh_token")
    response = client.post("/auth/refresh")

    assert response.status_code == 200

    body = response.json()
    assert body["access_token"] == "new_access_token"
    assert body["user_id"] == str(user.id)
    assert "refresh_token" in response.cookies

    mock_auth_service.refresh.assert_awaited_once_with("valid_refresh_token")


@pytest.mark.api
def test_refresh_missing_cookie(client, mock_auth_service):
    response = client.post("/auth/refresh")

    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Refresh token ausente"


@pytest.mark.api
def test_refresh_invalid_token(client, mock_auth_service):
    mock_auth_service.refresh.side_effect = ValueError("Refresh token inválido")

    client.cookies.set("refresh_token", "invalid_token")
    response = client.post("/auth/refresh")

    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Refresh token inválido"


@pytest.mark.api
def test_logout_success(authenticated_client):
    authenticated_client.cookies.set("refresh_token", "some_refresh_token")

    response = authenticated_client.post("/auth/logout")

    assert response.status_code == 204
    assert "refresh_token" not in response.cookies


@pytest.mark.api
def test_logout_unauthenticated(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401


@pytest.mark.api
def test_me_success(authenticated_client, user):
    response = authenticated_client.get("/auth/me")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == str(user.id)
    assert body["name"] == user.name
    assert body["email"] == user.email
    assert body["role"] == user.role.value


@pytest.mark.api
def test_me_unauthenticated(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
