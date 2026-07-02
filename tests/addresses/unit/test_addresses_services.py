import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.addresses.entity import Address
from src.modules.addresses.exceptions import AddressNotFoundException
from src.modules.addresses.schemas import (
    CreateAddressSchema,
    UpdateAddressSchema,
)
from src.modules.addresses.services import AddressService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def address_service(mock_repository):
    return AddressService(repository=mock_repository)


@pytest.fixture
def address():
    return Address(
        user_id=uuid.uuid4(),
        address_line="Rua das Flores",
        city="Recife",
        state="PE",
        number=100,
        district="Boa Viagem",
        complement="Apto 302",
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(address):
    return CreateAddressSchema(
        user_id=address.user_id,
        address_line=address.address_line,
        city=address.city,
        state=address.state,
        number=address.number,
        district=address.district,
        complement=address.complement,
    )


@pytest.fixture
def update_schema(address):
    return UpdateAddressSchema(
        id=address.id,
        user_id=address.user_id,
        address_line="Av. Boa Viagem",
        city="Recife",
        state="PE",
        number=200,
        district="Pina",
        complement="Casa",
    )


@pytest.mark.unit()
async def test_create_address(address_service, mock_repository, create_schema, address):
    mock_repository.create.return_value = address

    created = await address_service.create_address(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Address)
    assert created.city == address.city


@pytest.mark.unit()
async def test_get_all_addresses(address_service, mock_repository, address):
    mock_repository.get_all.return_value = [address, address]

    addresses = await address_service.get_all_addresses()

    mock_repository.get_all.assert_called_once()
    assert len(addresses) == 2


@pytest.mark.unit()
async def test_get_all_addresses_empty(address_service, mock_repository):
    mock_repository.get_all.return_value = []

    addresses = await address_service.get_all_addresses()

    mock_repository.get_all.assert_called_once()
    assert addresses == []


@pytest.mark.unit()
async def test_get_address_by_id(address_service, mock_repository, address):
    mock_repository.get_by_id.return_value = address

    found = await address_service.get_address_by_id(address.id)

    mock_repository.get_by_id.assert_called_once_with(address.id)
    assert found.id == address.id


@pytest.mark.unit()
async def test_get_address_by_id_not_found(address_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(AddressNotFoundException):
        await address_service.get_address_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_addresses_by_user_id(address_service, mock_repository, address):
    mock_repository.get_by_user_id.return_value = [address]

    addresses = await address_service.get_addresses_by_user_id(address.user_id)

    mock_repository.get_by_user_id.assert_called_once_with(address.user_id)
    assert len(addresses) == 1
    assert addresses[0].user_id == address.user_id


@pytest.mark.unit()
async def test_update_address(address_service, mock_repository, address, update_schema):
    updated = Address(
        user_id=update_schema.user_id,
        address_line=update_schema.address_line,
        city=update_schema.city,
        state=update_schema.state,
        number=update_schema.number,
        district=update_schema.district,
        complement=update_schema.complement,
        id=address.id,
    )
    mock_repository.get_by_id.return_value = address
    mock_repository.update_by_id.return_value = updated

    result = await address_service.update_address(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.address_line == update_schema.address_line


@pytest.mark.unit()
async def test_update_address_not_found(
    address_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(AddressNotFoundException):
        await address_service.update_address(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_address_by_id(address_service, mock_repository, address):
    mock_repository.get_by_id.return_value = address
    mock_repository.delete_by_id.return_value = True

    is_deleted = await address_service.delete_address_by_id(address.id)

    mock_repository.get_by_id.assert_called_once_with(address.id)
    mock_repository.delete_by_id.assert_called_once_with(address.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_address_by_id_not_found(address_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(AddressNotFoundException):
        await address_service.delete_address_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
