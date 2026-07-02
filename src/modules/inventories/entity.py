import uuid
from datetime import datetime


class Inventory:
    def __init__(
        self,
        product_id: uuid.UUID,
        quantity: int,
        updated_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.product_id = product_id
        self.quantity = quantity
        self.updated_at = updated_at
