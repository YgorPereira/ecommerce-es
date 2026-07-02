import uuid
from datetime import datetime


class Cart:
    def __init__(
        self,
        user_id: uuid.UUID,
        coupon_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.user_id = user_id
        self.coupon_id = coupon_id
        self.created_at = created_at
