from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from src.core.settings import settings
from src.database.session import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException
from src.modules.orders.repository import OrderRepository
from src.modules.payments.gateway import build_payment_gateway
from src.modules.payments.repository import PaymentRepository
from src.modules.payments.schemas import (
    CreatePaymentSchema,
    UpdatePaymentSchema,
    PaymentResponseSchema,
    PaymentWebhookSchema,
)
from src.modules.payments.services import PaymentService
from src.shared.exceptions import UnauthorizedException

payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    repository = PaymentRepository(db)
    return PaymentService(
        repository,
        build_payment_gateway(),
        OrderRepository(db),
    )


def verify_webhook_secret(
    x_webhook_secret: str | None = Header(default=None),
) -> None:
    """Autentica o webhook comparando um segredo compartilhado.

    Só é exigido quando ``WEBHOOK_SECRET`` está configurado no ambiente — assim,
    em desenvolvimento (sem segredo) o fluxo local continua aberto.
    """
    if settings.WEBHOOK_SECRET and x_webhook_secret != settings.WEBHOOK_SECRET:
        raise UnauthorizedException("Webhook não autorizado")


@payment_router.post(
    "",
    response_model=PaymentResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payment: CreatePaymentSchema,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_payment(payment)


@payment_router.post(
    "/webhook",
    response_model=PaymentResponseSchema,
)
async def payment_webhook(
    webhook: PaymentWebhookSchema,
    service: PaymentService = Depends(get_payment_service),
    _: None = Depends(verify_webhook_secret),
):
    """Confirmação assíncrona enviada pelo gateway de pagamento."""
    return await service.process_webhook(webhook.reference, webhook.status)


@payment_router.get(
    "",
    response_model=List[PaymentResponseSchema],
)
async def get_all_payments(
    service: PaymentService = Depends(get_payment_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_payments()


@payment_router.get(
    "/{payment_id}",
    response_model=PaymentResponseSchema,
)
async def get_payment_by_id(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
):
    payment = await service.get_payment_by_id(payment_id)
    order = await service.order_repository.get_by_id(payment.order_id)
    if not current_user.is_admin() and order.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return payment


@payment_router.get(
    "/order/{order_id}",
    response_model=List[PaymentResponseSchema],
)
async def get_payments_by_order_id(
    order_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
):
    order = await service.order_repository.get_by_id(order_id)
    if not current_user.is_admin() and order.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return await service.get_payments_by_order_id(order_id)


@payment_router.put(
    "",
    response_model=PaymentResponseSchema,
)
async def update_payment(
    payment: UpdatePaymentSchema,
    service: PaymentService = Depends(get_payment_service),
    _: User = Depends(require_admin),
):
    return await service.update_payment(payment)


@payment_router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_payment(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
):
    await service.delete_payment_by_id(payment_id)
