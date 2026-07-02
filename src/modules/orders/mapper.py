from src.modules.orders.entity import Order
from src.modules.orders.models import OrderModel


class OrderMapper:

    @staticmethod
    def to_model(entity: Order) -> OrderModel:
        return OrderModel(
            id=entity.id,
            user_id=entity.user_id,
            address_id=entity.address_id,
            coupon_id=entity.coupon_id,
            status=entity.status,
            created_at=entity.created_at,
            total_amount=entity.total_amount,
        )

    @staticmethod
    def to_entity(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            address_id=model.address_id,
            coupon_id=model.coupon_id,
            status=model.status,
            created_at=model.created_at,
            total_amount=model.total_amount,
        )
