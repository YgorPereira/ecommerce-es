import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.users.entity import User
from src.modules.users.enums.role import UserRole
from src.modules.users.exceptions import UserNotFoundException
from src.modules.users.schemas import CreateUserSchema, UpdateUserSchema
from src.modules.users.services import UserService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def user_service(mock_repository):
    return UserService(repository=mock_repository)


@pytest.fixture
def user():
    unique = str(uuid.uuid4())
    return User(
        name="Ygor",
        cpf='52998224725',
        email=f"{unique}@gmail.com",
        password="134fda1sd1ADFADF1",
        role=UserRole.COMMON,
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema():
    unique = str(uuid.uuid4())
    return CreateUserSchema(
        name="Ygor",
        cpf='52998224725',
        email=f"{unique}@gmail.com",
        password="134fda1sd1ADFADF1",
        role=UserRole.COMMON,
    )


@pytest.fixture
def update_schema(user):
    return UpdateUserSchema(
        id=user.id,
        name="Ygor Atualizado",
        email="ygor_atualizado@gmail.com",
        role=UserRole.ADMIN,
    )


@pytest.mark.unit()
async def test_create_user(user_service, mock_repository, create_schema, user):
    mock_repository.get_by_email.return_value = None
    mock_repository.create.return_value = user

    created_user = await user_service.create_user(create_schema)

    mock_repository.get_by_email.assert_called_once()
    mock_repository.create.assert_called_once()
    assert isinstance(created_user, User)
    assert created_user.name == user.name
    assert created_user.email == user.email
    assert created_user.role == user.role


@pytest.mark.unit()
async def test_get_all_users(user_service, mock_repository, user):
    second_user = User(
        name="Luana",
        cpf=str(uuid.uuid4())[:11],
        email="luana@gmail.com",
        password="senhaSegura123",
        role=UserRole.ADMIN,
        id=uuid.uuid4(),
    )
    mock_repository.get_all.return_value = [user, second_user]

    users = await user_service.get_all_users()

    mock_repository.get_all.assert_called_once()
    assert isinstance(users, list)
    assert len(users) == 2
    assert all(isinstance(u, User) for u in users)


@pytest.mark.unit()
async def test_get_all_users_empty(user_service, mock_repository):
    mock_repository.get_all.return_value = []

    users = await user_service.get_all_users()

    mock_repository.get_all.assert_called_once()
    assert users == []


@pytest.mark.unit()
async def test_get_user_by_id(user_service, mock_repository, user):
    mock_repository.get_by_id.return_value = user

    found_user = await user_service.get_user_by_id(user.id)

    mock_repository.get_by_id.assert_called_once_with(user.id)
    assert isinstance(found_user, User)
    assert found_user.id == user.id
    assert found_user.name == user.name
    assert found_user.email == user.email


@pytest.mark.unit()
async def test_get_user_by_id_not_found(user_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)

@pytest.mark.unit()
async def test_get_user_by_email(user_service, mock_repository, user):
    mock_repository.get_by_email.return_value = user

    found_user = await user_service.get_user_by_email(user.email)

    mock_repository.get_by_email.assert_called_once_with(user.email)
    assert isinstance(found_user, User)
    assert found_user.email == user.email


@pytest.mark.unit()
async def test_get_user_by_email_not_found(user_service, mock_repository):
    mock_repository.get_by_email.return_value = None

    with pytest.raises(UserNotFoundException):
            await user_service.get_user_by_email("nao_existe@gmail.com")

    mock_repository.get_by_email.assert_called_once_with("nao_existe@gmail.com")

@pytest.mark.unit()
async def test_update_user(user_service, mock_repository, user, update_schema):
    updated = User(
        name=update_schema.name,
        email=update_schema.email,
        cpf=user.cpf,
        password=user.password,
        role=update_schema.role,
        id=user.id,
    )
    mock_repository.update_by_id.return_value = updated

    result = await user_service.update_user(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert isinstance(result, User)
    assert result.name == update_schema.name
    assert result.email == update_schema.email
    assert result.role == update_schema.role


@pytest.mark.unit()
async def test_update_user_not_found(user_service, mock_repository, update_schema):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
            await user_service.update_user(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()

@pytest.mark.unit()
async def test_delete_user_by_id(user_service, mock_repository, user):
    mock_repository.get_by_id.return_value = user
    mock_repository.delete_by_id.return_value = True

    is_deleted = await user_service.delete_user_by_id(user.id)

    mock_repository.get_by_id.assert_called_once_with(user.id)
    mock_repository.delete_by_id.assert_called_once_with(user.id)
    assert is_deleted is True

@pytest.mark.unit()
async def test_delete_user_by_id_not_found(user_service, mock_repository):
    non_existent_id = uuid.uuid4()

    mock_repository.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
            await user_service.delete_user_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
    mock_repository.delete_user_by_id.assert_not_called()