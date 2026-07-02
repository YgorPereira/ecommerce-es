import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import CouponNotFoundException
from src.modules.coupons.router import get_coupon_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_coupon_service():
    service = AsyncMock()
    app.dependency_overrides[get_coupon_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def coupon():
    return Coupon(
        id=uuid.uuid4(),
        discount_percentage=10.0,
        discount_amount=5.0,
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        usage_limit=100,
    )


def _payload():
    return {
        "discount_percentage": 10.0,
        "discount_amount": 5.0,
        "expires_at": "2030-01-01T00:00:00+00:00",
        "usage_limit": 100,
    }


@pytest.mark.api
def test_create_coupon(client, mock_coupon_service, coupon):
    mock_coupon_service.create_coupon.return_value = coupon

    response = client.post("/coupons", json=_payload())

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(coupon.id)
    assert body["discount_percentage"] == coupon.discount_percentage
    assert body["usage_limit"] == coupon.usage_limit

    mock_coupon_service.create_coupon.assert_awaited_once()


@pytest.mark.api
def test_create_coupon_invalid_percentage(client):
    payload = _payload()
    payload["discount_percentage"] = 150.0

    response = client.post("/coupons", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_coupon_by_id(client, mock_coupon_service, coupon):
    mock_coupon_service.get_coupon_by_id.return_value = coupon

    response = client.get(f"/coupons/{coupon.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(coupon.id)


@pytest.mark.api
def test_get_coupon_by_id_not_found(client, mock_coupon_service):
    mock_coupon_service.get_coupon_by_id.side_effect = CouponNotFoundException()

    response = client.get(f"/coupons/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_all_coupons(client, mock_coupon_service, coupon):
    mock_coupon_service.get_all_coupons.return_value = [coupon, coupon]

    response = client.get("/coupons")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_coupons_empty(client, mock_coupon_service):
    mock_coupon_service.get_all_coupons.return_value = []

    response = client.get("/coupons")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_coupon(client, mock_coupon_service, coupon):
    mock_coupon_service.update_coupon.return_value = coupon

    payload = _payload()
    payload["id"] = str(coupon.id)

    response = client.put("/coupons", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == str(coupon.id)


@pytest.mark.api
def test_update_coupon_not_found(client, mock_coupon_service):
    mock_coupon_service.update_coupon.side_effect = CouponNotFoundException()

    payload = _payload()
    payload["id"] = str(uuid.uuid4())

    response = client.put("/coupons", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_delete_coupon(client, mock_coupon_service, coupon):
    mock_coupon_service.delete_coupon_by_id.return_value = True

    response = client.delete(f"/coupons/{coupon.id}")

    assert response.status_code == 204
    mock_coupon_service.delete_coupon_by_id.assert_awaited_once_with(coupon.id)


@pytest.mark.api
def test_delete_coupon_not_found(client, mock_coupon_service):
    mock_coupon_service.delete_coupon_by_id.side_effect = CouponNotFoundException()

    response = client.delete(f"/coupons/{uuid.uuid4()}")

    assert response.status_code == 404
