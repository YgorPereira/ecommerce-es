import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.core.settings import settings
from src.main import app
from src.modules.payments.entity import Payment
from src.modules.payments.exceptions import PaymentNotFoundException
from src.modules.payments.router import get_payment_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_payment_service():
    service = AsyncMock()
    app.dependency_overrides[get_payment_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def payment():
    return Payment(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        amount=250.0,
        method="credit_card",
        status="pending",
        gateway_reference=None,
        processed_at=None,
    )


def _payload(payment):
    return {
        "order_id": str(payment.order_id),
        "amount": payment.amount,
        "method": payment.method,
    }


@pytest.mark.api
def test_create_payment(client, mock_payment_service, payment):
    mock_payment_service.create_payment.return_value = payment

    response = client.post("/payments", json=_payload(payment))

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(payment.id)
    assert body["order_id"] == str(payment.order_id)
    assert body["status"] == "pending"
    assert body["processed_at"] is None

    mock_payment_service.create_payment.assert_awaited_once()


@pytest.mark.api
def test_create_payment_negative_amount(client, payment):
    payload = _payload(payment)
    payload["amount"] = -1.0

    response = client.post("/payments", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_payment_by_id(client, mock_payment_service, payment):
    mock_payment_service.get_payment_by_id.return_value = payment

    response = client.get(f"/payments/{payment.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(payment.id)


@pytest.mark.api
def test_get_payment_by_id_not_found(client, mock_payment_service):
    mock_payment_service.get_payment_by_id.side_effect = PaymentNotFoundException()

    response = client.get(f"/payments/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_payments_by_order_id(client, mock_payment_service, payment):
    mock_payment_service.get_payments_by_order_id.return_value = [payment]

    response = client.get(f"/payments/order/{payment.order_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["order_id"] == str(payment.order_id)


@pytest.mark.api
def test_get_all_payments(client, mock_payment_service, payment):
    mock_payment_service.get_all_payments.return_value = [payment, payment]

    response = client.get("/payments")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_payments_empty(client, mock_payment_service):
    mock_payment_service.get_all_payments.return_value = []

    response = client.get("/payments")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_payment(client, mock_payment_service, payment):
    payment.status = "paid"
    payment.gateway_reference = "ref-123"
    payment.processed_at = datetime.now(timezone.utc)
    mock_payment_service.update_payment.return_value = payment

    payload = _payload(payment)
    payload["id"] = str(payment.id)
    payload["status"] = "paid"
    payload["gateway_reference"] = "ref-123"

    response = client.put("/payments", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "paid"
    assert body["gateway_reference"] == "ref-123"
    assert body["processed_at"] is not None


@pytest.mark.api
def test_update_payment_not_found(client, mock_payment_service, payment):
    mock_payment_service.update_payment.side_effect = PaymentNotFoundException()

    payload = _payload(payment)
    payload["id"] = str(uuid.uuid4())
    payload["status"] = "paid"

    response = client.put("/payments", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_payment_webhook(client, mock_payment_service, payment):
    payment.status = "paid"
    payment.gateway_reference = "mp-123"
    payment.processed_at = datetime.now(timezone.utc)
    mock_payment_service.process_webhook.return_value = payment

    response = client.post(
        "/payments/webhook",
        json={"reference": "mp-123", "status": "approved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    mock_payment_service.process_webhook.assert_awaited_once_with("mp-123", "approved")


@pytest.mark.api
def test_payment_webhook_not_found(client, mock_payment_service):
    mock_payment_service.process_webhook.side_effect = PaymentNotFoundException()

    response = client.post(
        "/payments/webhook",
        json={"reference": "unknown", "status": "approved"},
    )

    assert response.status_code == 404


@pytest.mark.api
def test_payment_webhook_rejects_wrong_secret(
    client, mock_payment_service, monkeypatch
):
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "s3cr3t")

    response = client.post(
        "/payments/webhook",
        json={"reference": "mp-123", "status": "approved"},
    )

    assert response.status_code == 401
    mock_payment_service.process_webhook.assert_not_awaited()


@pytest.mark.api
def test_payment_webhook_accepts_correct_secret(
    client, mock_payment_service, payment, monkeypatch
):
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "s3cr3t")
    payment.status = "paid"
    mock_payment_service.process_webhook.return_value = payment

    response = client.post(
        "/payments/webhook",
        json={"reference": "mp-123", "status": "approved"},
        headers={"X-Webhook-Secret": "s3cr3t"},
    )

    assert response.status_code == 200
    mock_payment_service.process_webhook.assert_awaited_once()


@pytest.mark.api
def test_delete_payment(client, mock_payment_service, payment):
    mock_payment_service.delete_payment_by_id.return_value = True

    response = client.delete(f"/payments/{payment.id}")

    assert response.status_code == 204
    mock_payment_service.delete_payment_by_id.assert_awaited_once_with(payment.id)


@pytest.mark.api
def test_delete_payment_not_found(client, mock_payment_service):
    mock_payment_service.delete_payment_by_id.side_effect = PaymentNotFoundException()

    response = client.delete(f"/payments/{uuid.uuid4()}")

    assert response.status_code == 404
