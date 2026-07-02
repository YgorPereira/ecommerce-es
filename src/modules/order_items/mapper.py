from src.modules.order_items.entity import OrderItem
from src.modules.order_items.models import OrderItemModel
from src.modules.order_items.schemas import CreateOrderItemSchema


class OrderItemMapper:

    @staticmethod
    def to_model(entity: OrderItem) -> OrderItemModel:
        return OrderItemModel(
            id=entity.id,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            price=entity.price,
        )

    @staticmethod
    def to_entity(model: OrderItemModel) -> OrderItem:
        return OrderItem(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            price=model.price,
        )

    @staticmethod
    def from_create_schema(schema: CreateOrderItemSchema) -> OrderItem:
        return OrderItem(
            order_id=schema.order_id,
            product_id=schema.product_id,
            quantity=schema.quantity,
            price=schema.price,
        )
