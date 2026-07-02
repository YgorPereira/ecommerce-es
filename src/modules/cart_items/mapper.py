from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.models import CartItemModel
from src.modules.cart_items.schemas import CreateCartItemSchema


class CartItemMapper:

    @staticmethod
    def to_model(entity: CartItem) -> CartItemModel:
        return CartItemModel(
            id=entity.id,
            cart_id=entity.cart_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
        )

    @staticmethod
    def to_entity(model: CartItemModel) -> CartItem:
        return CartItem(
            id=model.id,
            cart_id=model.cart_id,
            product_id=model.product_id,
            quantity=model.quantity,
        )

    @staticmethod
    def from_create_schema(schema: CreateCartItemSchema) -> CartItem:
        return CartItem(
            cart_id=schema.cart_id,
            product_id=schema.product_id,
            quantity=schema.quantity,
        )
