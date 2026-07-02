import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.addresses.entity import Address
from src.modules.addresses.exceptions import AddressNotFoundException
from src.modules.addresses.router import get_address_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_address_service():
    service = AsyncMock()
    app.dependency_overrides[get_address_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def address():
    return Address(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        address_line="Rua das Flores",
        city="Recife",
        state="PE",
        number=100,
        district="Boa Viagem",
        complement="Apto 302",
    )


def _payload(address):
    return {
        "user_id": str(address.user_id),
        "address_line": address.address_line,
        "city": address.city,
        "state": address.state,
        "number": address.number,
        "district": address.district,
        "complement": address.complement,
    }


@pytest.mark.api
def test_create_address(client, mock_address_service, address):
    mock_address_service.create_address.return_value = address

    response = client.post("/addresses", json=_payload(address))

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(address.id)
    assert body["user_id"] == str(address.user_id)
    assert body["city"] == address.city

    mock_address_service.create_address.assert_awaited_once()


@pytest.mark.api
def test_create_address_invalid_number(client, address):
    payload = _payload(address)
    payload["number"] = 0

    response = client.post("/addresses", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_address_by_id(client, mock_address_service, address):
    mock_address_service.get_address_by_id.return_value = address

    response = client.get(f"/addresses/{address.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(address.id)


@pytest.mark.api
def test_get_address_by_id_not_found(client, mock_address_service):
    mock_address_service.get_address_by_id.side_effect = AddressNotFoundException()

    response = client.get(f"/addresses/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_addresses_by_user_id(client, mock_address_service, address):
    mock_address_service.get_addresses_by_user_id.return_value = [address]

    response = client.get(f"/addresses/user/{address.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["user_id"] == str(address.user_id)


@pytest.mark.api
def test_get_all_addresses(client, mock_address_service, address):
    mock_address_service.get_all_addresses.return_value = [address, address]

    response = client.get("/addresses")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_addresses_empty(client, mock_address_service):
    mock_address_service.get_all_addresses.return_value = []

    response = client.get("/addresses")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_address(client, mock_address_service, address):
    mock_address_service.update_address.return_value = address

    payload = _payload(address)
    payload["id"] = str(address.id)

    response = client.put("/addresses", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == str(address.id)


@pytest.mark.api
def test_update_address_not_found(client, mock_address_service, address):
    mock_address_service.update_address.side_effect = AddressNotFoundException()

    payload = _payload(address)
    payload["id"] = str(uuid.uuid4())

    response = client.put("/addresses", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_delete_address(client, mock_address_service, address):
    mock_address_service.delete_address_by_id.return_value = True

    response = client.delete(f"/addresses/{address.id}")

    assert response.status_code == 204
    mock_address_service.delete_address_by_id.assert_awaited_once_with(address.id)


@pytest.mark.api
def test_delete_address_not_found(client, mock_address_service):
    mock_address_service.delete_address_by_id.side_effect = AddressNotFoundException()

    response = client.delete(f"/addresses/{uuid.uuid4()}")

    assert response.status_code == 404
