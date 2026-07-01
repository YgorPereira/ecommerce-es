import pytest
from pydantic import ValidationError

from src.modules.users.enums.role import UserRole
from src.modules.users.schemas import CreateUserSchema, UpdateUserSchema
import uuid

# ---------------------------------------------------------------------------
# CreateUserSchema — CPF
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_create_schema_cpf_valid():
    schema = CreateUserSchema(
        name="Ygor",
        cpf="52998224725",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )
    assert schema.cpf == "52998224725"


@pytest.mark.unit()
def test_create_schema_cpf_with_formatting():
    schema = CreateUserSchema(
        name="Ygor",
        cpf="529.982.247-25",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )
    assert schema.cpf == "52998224725"


@pytest.mark.unit()
def test_create_schema_cpf_all_same_digits():
    with pytest.raises(ValidationError) as exc:
        CreateUserSchema(
            name="Ygor",
            cpf="00000000000",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )
    assert "CPF inválido" in str(exc.value)


@pytest.mark.unit()
def test_create_schema_cpf_wrong_verifier():
    with pytest.raises(ValidationError) as exc:
        CreateUserSchema(
            name="Ygor",
            cpf="12345678900",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )
    assert "CPF inválido" in str(exc.value)


@pytest.mark.unit()
def test_create_schema_cpf_too_short():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="1234567",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )


@pytest.mark.unit()
def test_create_schema_cpf_with_letters():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="ABC.DEF.GHI-JK",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )


# ---------------------------------------------------------------------------
# CreateUserSchema — Email
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_create_schema_email_valid():
    schema = CreateUserSchema(
        name="Ygor",
        cpf="52998224725",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )
    assert schema.email == "ygor@gmail.com"


@pytest.mark.unit()
def test_create_schema_email_missing_at():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="52998224725",
            email="ygorgmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )


@pytest.mark.unit()
def test_create_schema_email_missing_domain():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="52998224725",
            email="ygor@",
            password="senha1234",
            role=UserRole.COMMON,
        )


@pytest.mark.unit()
def test_create_schema_email_empty():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="52998224725",
            email="",
            password="senha1234",
            role=UserRole.COMMON,
        )


# ---------------------------------------------------------------------------
# CreateUserSchema — Password
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_create_schema_password_valid():
    schema = CreateUserSchema(
        name="Ygor",
        cpf="52998224725",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )
    assert schema.password == "senha1234"


@pytest.mark.unit()
def test_create_schema_password_too_short():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="52998224725",
            email="ygor@gmail.com",
            password="123",
            role=UserRole.COMMON,
        )


@pytest.mark.unit()
def test_create_schema_password_empty():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="Ygor",
            cpf="52998224725",
            email="ygor@gmail.com",
            password="",
            role=UserRole.COMMON,
        )


# ---------------------------------------------------------------------------
# CreateUserSchema — Name
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_create_schema_name_valid():
    schema = CreateUserSchema(
        name="Ygor",
        cpf="52998224725",
        email="ygor@gmail.com",
        password="senha1234",
        role=UserRole.COMMON,
    )
    assert schema.name == "Ygor"


@pytest.mark.unit()
def test_create_schema_name_too_short():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="AB",
            cpf="52998224725",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )


@pytest.mark.unit()
def test_create_schema_name_empty():
    with pytest.raises(ValidationError):
        CreateUserSchema(
            name="",
            cpf="52998224725",
            email="ygor@gmail.com",
            password="senha1234",
            role=UserRole.COMMON,
        )


# ---------------------------------------------------------------------------
# UpdateUserSchema
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateUserSchema(
        id=uuid.uuid4(),
        name="Ygor Atualizado",
        email="ygor_atualizado@gmail.com",
        role=UserRole.ADMIN,
    )
    assert schema.name == "Ygor Atualizado"
    assert schema.role == UserRole.ADMIN


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateUserSchema(
            name="Ygor Atualizado",
            email="ygor_atualizado@gmail.com",
            role=UserRole.ADMIN,
        )


@pytest.mark.unit()
def test_update_schema_invalid_email():
    with pytest.raises(ValidationError):
        UpdateUserSchema(
            id=uuid.uuid4(),
            name="Ygor Atualizado",
            email="email_invalido",
            role=UserRole.ADMIN,
        )


@pytest.mark.unit()
def test_update_schema_name_too_short():
    with pytest.raises(ValidationError):
        UpdateUserSchema(
            id=uuid.uuid4(),
            name="AB",
            email="ygor@gmail.com",
            role=UserRole.ADMIN,
        )
