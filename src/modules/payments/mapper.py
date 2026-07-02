from src.modules.payments.entity import Payment
from src.modules.payments.models import PaymentModel


class PaymentMapper:

    @staticmethod
    def to_model(entity: Payment) -> PaymentModel:
        return PaymentModel(
            id=entity.id,
            order_id=entity.order_id,
            amount=entity.amount,
            method=entity.method,
            status=entity.status,
            gateway_reference=entity.gateway_reference,
            processed_at=entity.processed_at,
        )

    @staticmethod
    def to_entity(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            order_id=model.order_id,
            amount=model.amount,
            method=model.method,
            status=model.status,
            gateway_reference=model.gateway_reference,
            processed_at=model.processed_at,
        )
