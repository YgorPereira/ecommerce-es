from src.modules.carts.entity import Cart
from src.modules.carts.models import CartModel


class CartMapper:

    @staticmethod
    def to_model(entity: Cart) -> CartModel:
        return CartModel(
            id=entity.id,
            user_id=entity.user_id,
            coupon_id=entity.coupon_id,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_entity(model: CartModel) -> Cart:
        return Cart(
            id=model.id,
            user_id=model.user_id,
            coupon_id=model.coupon_id,
            created_at=model.created_at,
        )
