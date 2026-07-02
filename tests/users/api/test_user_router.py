import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.modules.users.enums.role import UserRole
from src.modules.users.exceptions import (
    UserEmailAlreadyExistsException,
    UserNotFoundException,
)
from src.modules.users.router import get_user_service


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_user_service():
    service = AsyncMock()
    app.dependency_overrides[get_user_service] = lambda: service
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
def admin():
    return User(
        id=uuid.uuid4(),
        name="Admin",
        cpf="52998224725",
        email="admin@gmail.com",
        password="senha1234",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def authenticated_client(client, user):
    app.dependency_overrides[get_current_user] = lambda: user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_client(client, admin):
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin
    yield client
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.mark.api
def test_create_user(client, mock_user_service, user):
    mock_user_service.create_user.return_value = user

    response = client.post(
        "/users",
        json={
            "name": user.name,
            "cpf": user.cpf,
            "role": user.role.value,
            "email": user.email,
            "password": "senha1234",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(user.id)
    assert body["name"] == user.name
    assert body["cpf"] == user.cpf
    assert body["email"] == user.email
    assert body["role"] == user.role.value

    mock_user_service.create_user.assert_awaited_once()


@pytest.mark.api
def test_create_user_email_already_exists(client, mock_user_service):
    mock_user_service.create_user.side_effect = UserEmailAlreadyExistsException()

    response = client.post(
        "/users",
        json={
            "name": "Ygor",
            "cpf": "52998224725",
            "email": "ygor@gmail.com",
            "password": "senha1234",
            "role": UserRole.COMMON.value,
        },
    )

    assert response.status_code == 409


@pytest.mark.api
def test_create_user_invalid_email(client):
    response = client.post(
        "/users",
        json={
            "name": "Ygor",
            "cpf": "52998224725",
            "email": "email_invalido",
            "password": "senha1234",
            "role": UserRole.COMMON.value,
        },
    )

    assert response.status_code == 422


@pytest.mark.api
def test_get_user_by_id_as_owner(authenticated_client, mock_user_service, user):
    mock_user_service.get_user_by_id.return_value = user
    app.dependency_overrides[get_current_user] = lambda: user

    response = authenticated_client.get(f"/users/{user.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["name"] == user.name
    assert body["email"] == user.email


@pytest.mark.api
def test_get_user_by_id_as_admin(admin_client, mock_user_service, user):
    mock_user_service.get_user_by_id.return_value = user

    response = admin_client.get(f"/users/{user.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)


@pytest.mark.api
def test_get_user_by_id_forbidden(authenticated_client, mock_user_service):
    other_id = uuid.uuid4()

    response = authenticated_client.get(f"/users/{other_id}")

    assert response.status_code == 401


@pytest.mark.api
def test_get_user_by_id_not_found(admin_client, mock_user_service):
    mock_user_service.get_user_by_id.side_effect = UserNotFoundException()

    response = admin_client.get(f"/users/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_user_by_id_unauthenticated(client, mock_user_service):
    response = client.get(f"/users/{uuid.uuid4()}")

    assert response.status_code == 401


@pytest.mark.api
def test_get_user_by_email_as_owner(authenticated_client, mock_user_service, user):
    mock_user_service.get_user_by_email.return_value = user
    app.dependency_overrides[get_current_user] = lambda: user

    response = authenticated_client.get(f"/users/email/{user.email}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == user.email


@pytest.mark.api
def test_get_user_by_email_as_admin(admin_client, mock_user_service, user):
    mock_user_service.get_user_by_email.return_value = user

    response = admin_client.get(f"/users/email/{user.email}")

    assert response.status_code == 200


@pytest.mark.api
def test_get_user_by_email_forbidden(authenticated_client, mock_user_service):
    response = authenticated_client.get("/users/email/outro@gmail.com")

    assert response.status_code == 401


@pytest.mark.api
def test_get_user_by_email_not_found(admin_client, mock_user_service):
    mock_user_service.get_user_by_email.side_effect = UserNotFoundException()

    response = admin_client.get("/users/email/naoexiste@gmail.com")

    assert response.status_code == 404


@pytest.mark.api
def test_get_all_users_as_admin(admin_client, mock_user_service, user):
    mock_user_service.get_all_users.return_value = [user, user]

    response = admin_client.get("/users")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == str(user.id)


@pytest.mark.api
def test_get_all_users_forbidden(authenticated_client, mock_user_service, user):
    response = authenticated_client.get("/users")

    assert response.status_code == 401


@pytest.mark.api
def test_get_all_users_unauthenticated(client, mock_user_service):
    response = client.get("/users")

    assert response.status_code == 401


@pytest.mark.api
def test_get_all_users_empty(admin_client, mock_user_service):
    mock_user_service.get_all_users.return_value = []

    response = admin_client.get("/users")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_user_as_owner(authenticated_client, mock_user_service, user):
    mock_user_service.update_user.return_value = user
    app.dependency_overrides[get_current_user] = lambda: user

    response = authenticated_client.put(
        "/users",
        json={
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)


@pytest.mark.api
def test_update_user_as_admin(admin_client, mock_user_service, user):
    mock_user_service.update_user.return_value = user

    response = admin_client.put(
        "/users",
        json={
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
        },
    )

    assert response.status_code == 200


@pytest.mark.api
def test_update_user_forbidden(authenticated_client, mock_user_service):
    response = authenticated_client.put(
        "/users",
        json={
            "id": str(uuid.uuid4()),
            "name": "Outro",
            "email": "outro@gmail.com",
            "role": UserRole.COMMON.value,
        },
    )

    assert response.status_code == 401


@pytest.mark.api
def test_update_user_not_found(admin_client, mock_user_service):
    mock_user_service.update_user.side_effect = UserNotFoundException()

    response = admin_client.put(
        "/users",
        json={
            "id": str(uuid.uuid4()),
            "name": "Ygor",
            "email": "ygor@gmail.com",
            "role": UserRole.COMMON.value,
        },
    )

    assert response.status_code == 404


@pytest.mark.api
def test_delete_user_as_admin(admin_client, mock_user_service, user):
    mock_user_service.delete_user_by_id.return_value = True

    response = admin_client.delete(f"/users/{user.id}")

    assert response.status_code == 204
    mock_user_service.delete_user_by_id.assert_awaited_once_with(user.id)


@pytest.mark.api
def test_delete_user_forbidden(authenticated_client, mock_user_service, user):
    response = authenticated_client.delete(f"/users/{user.id}")

    assert response.status_code == 401


@pytest.mark.api
def test_delete_user_unauthenticated(client, mock_user_service, user):
    response = client.delete(f"/users/{user.id}")

    assert response.status_code == 401


@pytest.mark.api
def test_delete_user_not_found(admin_client, mock_user_service):
    mock_user_service.delete_user_by_id.side_effect = UserNotFoundException()

    response = admin_client.delete(f"/users/{uuid.uuid4()}")

    assert response.status_code == 404
