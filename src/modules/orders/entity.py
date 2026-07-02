import uuid
from datetime import datetime


class Order:
    def __init__(
        self,
        user_id: uuid.UUID,
        address_id: uuid.UUID,
        total_amount: float,
        status: str,
        coupon_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.user_id = user_id
        self.address_id = address_id
        self.coupon_id = coupon_id
        self.status = status
        self.created_at = created_at
        self.total_amount = total_amount
