import uuid


class OrderItem:
    def __init__(
        self,
        order_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
        price: float,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
