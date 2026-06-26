import uuid

import pytest

from src.modules.users.models import UserModel
from src.modules.users.enums.role import UserRole


@pytest.fixture
def user():
    unique = str(uuid.uuid4())

    return UserModel(
        name="Ygor",
        cpf=unique[:11],
        email=f"{unique}@gmail.com",
        password="134fda1sd1ADFADF1",
        role=UserRole.COMMON,
    )


@pytest.fixture(scope="function")
def persisted_user(user_repository, user):
    return user_repository.create(user)


@pytest.mark.integration()
def test_create_user(user_repository, user):
    created_user = user_repository.create(user)

    assert created_user.name == user.name
    assert created_user.cpf == user.cpf
    assert created_user.email == user.email
    assert created_user.password == user.password
    assert created_user.role == user.role


@pytest.mark.integration()
def test_get_user_by_id(user_repository, persisted_user, user):
    found_user = user_repository.get_by_id(persisted_user.id)

    assert found_user.name == user.name
    assert found_user.cpf == user.cpf
    assert found_user.email == user.email
    assert found_user.password == user.password
    assert found_user.role == user.role


@pytest.mark.integration()
def test_get_user_by_email(user_repository, persisted_user, user):
    found_user = user_repository.get_by_email(persisted_user.email)

    assert found_user.id == persisted_user.id
    assert found_user.name == persisted_user.name
    assert found_user.cpf == persisted_user.cpf
    assert found_user.email == persisted_user.email
    assert found_user.password == persisted_user.password
    assert found_user.role == persisted_user.role


@pytest.mark.integration()
def test_update_user_by_id(user_repository, persisted_user):
    persisted_user.name = "Luana"
    persisted_user.email = "luana@gmail.com"
    persisted_user.role = UserRole.ADMIN

    updated_user = user_repository.update_by_id(persisted_user)

    assert updated_user.id == persisted_user.id
    assert updated_user.name == "Luana"
    assert updated_user.email == "luana@gmail.com"
    assert updated_user.role == UserRole.ADMIN


@pytest.mark.integration()
def test_delete_user_by_id(user_repository, persisted_user):
    is_deleted = user_repository.delete_by_id(persisted_user.id)

    assert is_deleted


@pytest.mark.integration()
def test_get_all_users_empty(user_repository):
    users = user_repository.get_all()
    assert users == []


@pytest.mark.integration()
def test_get_all_users(user_repository, user):
    second_unique = str(uuid.uuid4())
    second_user = UserModel(
        name="Luana",
        cpf=second_unique[:11],
        email=f"{second_unique}@gmail.com",
        password="senha_segura_123",
        role=UserRole.ADMIN,
    )
    user_repository.create(user)
    user_repository.create(second_user)

    users = user_repository.get_all()

    assert len(users) == 2
    emails = [u.email for u in users]
    assert user.email in emails
    assert second_user.email in emails


@pytest.mark.integration()
def test_get_user_by_id_not_found(user_repository):
    non_existent_id = uuid.uuid4()
    found_user = user_repository.get_by_id(non_existent_id)
    assert found_user is None


@pytest.mark.integration()
def test_get_user_by_email_not_found(user_repository):
    found_user = user_repository.get_by_email("nao_existe@gmail.com")
    assert found_user is None


@pytest.mark.integration()
def test_delete_user_by_id_not_found(user_repository):
    non_existent_id = uuid.uuid4()
    is_deleted = user_repository.delete_by_id(non_existent_id)
    assert not is_deleted
