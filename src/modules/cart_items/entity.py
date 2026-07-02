import uuid


class CartItem:
    def __init__(
        self,
        cart_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity
