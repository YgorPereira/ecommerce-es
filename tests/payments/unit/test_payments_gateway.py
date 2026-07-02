import uuid

import pytest

from src.modules.payments.gateway import (
    GatewayResult,
    StubGateway,
    map_gateway_status,
)


@pytest.mark.unit()
@pytest.mark.parametrize(
    "gateway_status,expected",
    [
        ("approved", "paid"),
        ("accredited", "paid"),
        ("rejected", "failed"),
        ("cancelled", "failed"),
        ("refunded", "failed"),
        ("pending", "pending"),
        ("in_process", "pending"),
    ],
)
def test_map_gateway_status(gateway_status, expected):
    assert map_gateway_status(gateway_status) == expected


@pytest.mark.unit()
async def test_stub_gateway_returns_reference():
    gateway = StubGateway()
    order_id = uuid.uuid4()

    result = await gateway.create_payment(order_id=order_id, amount=100.0, method="pix")

    assert isinstance(result, GatewayResult)
    assert result.reference == f"stub-{order_id}"
    assert result.status == "pending"
