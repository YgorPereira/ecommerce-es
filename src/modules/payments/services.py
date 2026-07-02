from datetime import datetime, timezone
from typing import List
import uuid

from src.modules.payments.entity import Payment
from src.modules.payments.exceptions import (
    PaymentGatewayException,
    PaymentNotFoundException,
)
from src.modules.orders.entity import Order
from src.modules.orders.repository import OrderRepository
from src.modules.orders.services import PAID_ORDER_STATUS
from src.modules.payments.gateway import (
    PaymentGateway,
    PaymentGatewayError,
    map_gateway_status,
)
from src.modules.payments.repository import PaymentRepository
from src.modules.payments.schemas import (
    CreatePaymentSchema,
    UpdatePaymentSchema,
)

PAID_PAYMENT_STATUS = "paid"


class PaymentService:
    def __init__(
        self,
        repository: PaymentRepository,
        gateway: PaymentGateway,
        order_repository: OrderRepository,
    ):
        self.repository = repository
        self.gateway = gateway
        self.order_repository = order_repository

    async def create_payment(self, payment: CreatePaymentSchema) -> Payment:
        """Inicia o pagamento no gateway e persiste o registro local.

        O ``gateway_reference`` retornado é guardado para casar a confirmação
        assíncrona (webhook) com este pagamento mais tarde.
        """
        try:
            result = await self.gateway.create_payment(
                order_id=payment.order_id,
                amount=payment.amount,
                method=payment.method,
            )
        except PaymentGatewayError as exc:
            raise PaymentGatewayException(str(exc)) from exc

        return await self.repository.create(
            Payment(
                order_id=payment.order_id,
                amount=payment.amount,
                method=payment.method,
                status=map_gateway_status(result.status),
                gateway_reference=result.reference,
            )
        )

    async def process_webhook(
        self, reference: str, gateway_status: str
    ) -> Payment | None:
        """Confirma o pagamento de forma assíncrona (chamado pelo gateway).

        Localiza o pagamento pelo ``gateway_reference``, traduz o status do
        gateway e marca o ``processed_at``.
        """
        db_item = await self.repository.get_by_reference(reference)

        if db_item is None:
            raise PaymentNotFoundException()

        new_status = map_gateway_status(gateway_status)

        updated = await self.repository.update_by_id(
            Payment(
                id=db_item.id,
                order_id=db_item.order_id,
                amount=db_item.amount,
                method=db_item.method,
                status=new_status,
                gateway_reference=reference,
                processed_at=datetime.now(timezone.utc),
            )
        )

        if new_status == PAID_PAYMENT_STATUS:
            await self._mark_order_paid(db_item.order_id)

        return updated

    async def _mark_order_paid(self, order_id: uuid.UUID) -> None:
        order = await self.order_repository.get_by_id(order_id)

        if order is None:
            return

        await self.order_repository.update_by_id(
            Order(
                id=order.id,
                user_id=order.user_id,
                address_id=order.address_id,
                coupon_id=order.coupon_id,
                total_amount=order.total_amount,
                status=PAID_ORDER_STATUS,
                created_at=order.created_at,
            )
        )

    async def get_all_payments(self) -> List[Payment]:
        return await self.repository.get_all()

    async def get_payment_by_id(self, id: uuid.UUID) -> Payment:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise PaymentNotFoundException()

        return db_item

    async def get_payments_by_order_id(self, order_id: uuid.UUID) -> List[Payment]:
        return await self.repository.get_by_order_id(order_id)

    async def update_payment(self, payment: UpdatePaymentSchema) -> Payment | None:
        db_item = await self.repository.get_by_id(payment.id)

        if db_item is None:
            raise PaymentNotFoundException()

        return await self.repository.update_by_id(
            Payment(
                id=payment.id,
                order_id=payment.order_id,
                amount=payment.amount,
                method=payment.method,
                status=payment.status,
                gateway_reference=payment.gateway_reference,
                processed_at=datetime.now(timezone.utc),
            )
        )

    async def delete_payment_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise PaymentNotFoundException()

        return await self.repository.delete_by_id(id)
