"""Camada de integração com o gateway de pagamento (Mercado Pago).

Abstrai o gateway atrás de um `Protocol` para manter o `PaymentService`
desacoplado e testável (mockável). Em produção usa o `MercadoPagoGateway`
(chamadas HTTP reais); sem token configurado, cai no `StubGateway`, que não
faz nenhuma chamada externa — ideal para desenvolvimento e testes locais.
"""

from dataclasses import dataclass
from typing import Protocol
import uuid

import httpx

from src.core.settings import settings


class PaymentGatewayError(Exception):
    """Falha ao comunicar com o gateway de pagamento."""


@dataclass
class GatewayResult:
    reference: str
    status: str


_APPROVED_STATUSES = {"approved", "paid", "accredited"}
_FAILED_STATUSES = {"rejected", "cancelled", "canceled", "refunded", "charged_back"}


def map_gateway_status(gateway_status: str) -> str:
    """Traduz o status do gateway para o status interno do pedido/pagamento."""
    normalized = gateway_status.lower()

    if normalized in _APPROVED_STATUSES:
        return "paid"

    if normalized in _FAILED_STATUSES:
        return "failed"

    return "pending"


class PaymentGateway(Protocol):
    async def create_payment(
        self, *, order_id: uuid.UUID, amount: float, method: str
    ) -> GatewayResult: ...


class MercadoPagoGateway:
    def __init__(self, access_token: str, api_url: str):
        self._access_token = access_token
        self._api_url = api_url.rstrip("/")

    async def create_payment(
        self, *, order_id: uuid.UUID, amount: float, method: str
    ) -> GatewayResult:
        if not self._access_token:
            raise PaymentGatewayError("Mercado Pago access token não configurado")

        payload = {
            "transaction_amount": amount,
            "payment_method_id": method,
            "external_reference": str(order_id),
            "description": f"Pedido {order_id}",
        }
        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self._api_url}/v1/payments",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise PaymentGatewayError(
                f"Falha ao comunicar com o Mercado Pago: {exc}"
            ) from exc

        return GatewayResult(
            reference=str(data.get("id")),
            status=str(data.get("status", "pending")),
        )


class StubGateway:
    """Gateway de desenvolvimento: não faz chamadas externas."""

    async def create_payment(
        self, *, order_id: uuid.UUID, amount: float, method: str
    ) -> GatewayResult:
        return GatewayResult(reference=f"stub-{order_id}", status="pending")


def build_payment_gateway() -> PaymentGateway:
    if settings.MERCADO_PAGO_ACCESS_TOKEN:
        return MercadoPagoGateway(
            settings.MERCADO_PAGO_ACCESS_TOKEN,
            settings.MERCADO_PAGO_API_URL,
        )

    return StubGateway()
