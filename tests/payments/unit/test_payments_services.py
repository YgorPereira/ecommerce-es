import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.orders.entity import Order
from src.modules.payments.entity import Payment
from src.modules.payments.exceptions import (
    PaymentGatewayException,
    PaymentNotFoundException,
)
from src.modules.payments.gateway import GatewayResult, PaymentGatewayError
from src.modules.payments.schemas import (
    CreatePaymentSchema,
    UpdatePaymentSchema,
)
from src.modules.payments.services import PaymentService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_gateway():
    gateway = AsyncMock()
    gateway.create_payment.return_value = GatewayResult(
        reference="mp-123", status="pending"
    )
    return gateway


@pytest.fixture
def mock_order_repository():
    return AsyncMock()


@pytest.fixture
def payment_service(mock_repository, mock_gateway, mock_order_repository):
    return PaymentService(
        repository=mock_repository,
        gateway=mock_gateway,
        order_repository=mock_order_repository,
    )


@pytest.fixture
def payment():
    return Payment(
        order_id=uuid.uuid4(),
        amount=250.0,
        method="credit_card",
        status="pending",
        gateway_reference="mp-123",
        processed_at=None,
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(payment):
    return CreatePaymentSchema(
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
    )


@pytest.fixture
def update_schema(payment):
    return UpdatePaymentSchema(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
        status="paid",
        gateway_reference="mp-123",
    )


async def _echo(entity):
    return entity


@pytest.mark.unit()
async def test_create_payment_initiates_gateway(
    payment_service, mock_repository, mock_gateway, create_schema
):
    mock_repository.create.side_effect = _echo

    created = await payment_service.create_payment(create_schema)

    mock_gateway.create_payment.assert_awaited_once()
    assert created.gateway_reference == "mp-123"
    assert created.status == "pending"


@pytest.mark.unit()
async def test_create_payment_maps_approved_status(
    payment_service, mock_repository, mock_gateway, create_schema
):
    mock_gateway.create_payment.return_value = GatewayResult(
        reference="mp-9", status="approved"
    )
    mock_repository.create.side_effect = _echo

    created = await payment_service.create_payment(create_schema)

    assert created.status == "paid"
    assert created.gateway_reference == "mp-9"


@pytest.mark.unit()
async def test_create_payment_gateway_failure(
    payment_service, mock_repository, mock_gateway, create_schema
):
    mock_gateway.create_payment.side_effect = PaymentGatewayError("boom")

    with pytest.raises(PaymentGatewayException):
        await payment_service.create_payment(create_schema)

    mock_repository.create.assert_not_called()


@pytest.mark.unit()
async def test_process_webhook_marks_paid(payment_service, mock_repository, payment):
    mock_repository.get_by_reference.return_value = payment
    mock_repository.update_by_id.side_effect = _echo

    result = await payment_service.process_webhook("mp-123", "approved")

    mock_repository.get_by_reference.assert_awaited_once_with("mp-123")
    assert result.status == "paid"
    assert result.processed_at is not None


@pytest.mark.unit()
async def test_process_webhook_marks_failed(payment_service, mock_repository, payment):
    mock_repository.get_by_reference.return_value = payment
    mock_repository.update_by_id.side_effect = _echo

    result = await payment_service.process_webhook("mp-123", "rejected")

    assert result.status == "failed"


@pytest.mark.unit()
async def test_process_webhook_not_found(payment_service, mock_repository):
    mock_repository.get_by_reference.return_value = None

    with pytest.raises(PaymentNotFoundException):
        await payment_service.process_webhook("unknown", "approved")

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_process_webhook_marks_order_paid(
    payment_service, mock_repository, mock_order_repository, payment
):
    mock_repository.get_by_reference.return_value = payment
    mock_repository.update_by_id.side_effect = _echo
    mock_order_repository.get_by_id.return_value = Order(
        user_id=uuid.uuid4(),
        address_id=uuid.uuid4(),
        total_amount=250.0,
        status="pending",
        created_at=datetime.now(timezone.utc),
        id=payment.order_id,
    )

    await payment_service.process_webhook("mp-123", "approved")

    mock_order_repository.update_by_id.assert_awaited_once()
    updated_order = mock_order_repository.update_by_id.call_args.args[0]
    assert updated_order.status == "paid"


@pytest.mark.unit()
async def test_process_webhook_failed_does_not_pay_order(
    payment_service, mock_repository, mock_order_repository, payment
):
    mock_repository.get_by_reference.return_value = payment
    mock_repository.update_by_id.side_effect = _echo

    await payment_service.process_webhook("mp-123", "rejected")

    mock_order_repository.update_by_id.assert_not_awaited()


@pytest.mark.unit()
async def test_get_all_payments(payment_service, mock_repository, payment):
    mock_repository.get_all.return_value = [payment, payment]

    payments = await payment_service.get_all_payments()

    mock_repository.get_all.assert_called_once()
    assert len(payments) == 2


@pytest.mark.unit()
async def test_get_payment_by_id(payment_service, mock_repository, payment):
    mock_repository.get_by_id.return_value = payment

    found = await payment_service.get_payment_by_id(payment.id)

    mock_repository.get_by_id.assert_called_once_with(payment.id)
    assert found.id == payment.id


@pytest.mark.unit()
async def test_get_payment_by_id_not_found(payment_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(PaymentNotFoundException):
        await payment_service.get_payment_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_payments_by_order_id(payment_service, mock_repository, payment):
    mock_repository.get_by_order_id.return_value = [payment]

    payments = await payment_service.get_payments_by_order_id(payment.order_id)

    mock_repository.get_by_order_id.assert_called_once_with(payment.order_id)
    assert len(payments) == 1


@pytest.mark.unit()
async def test_update_payment_sets_processed_at(
    payment_service, mock_repository, payment, update_schema
):
    mock_repository.get_by_id.return_value = payment
    mock_repository.update_by_id.side_effect = _echo

    result = await payment_service.update_payment(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.status == "paid"
    assert result.processed_at is not None


@pytest.mark.unit()
async def test_update_payment_not_found(
    payment_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(PaymentNotFoundException):
        await payment_service.update_payment(update_schema)

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_payment_by_id(payment_service, mock_repository, payment):
    mock_repository.get_by_id.return_value = payment
    mock_repository.delete_by_id.return_value = True

    is_deleted = await payment_service.delete_payment_by_id(payment.id)

    mock_repository.delete_by_id.assert_called_once_with(payment.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_payment_by_id_not_found(payment_service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(PaymentNotFoundException):
        await payment_service.delete_payment_by_id(uuid.uuid4())
