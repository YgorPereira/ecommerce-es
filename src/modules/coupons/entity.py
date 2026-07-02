import uuid
from datetime import datetime


class Coupon:
    def __init__(
        self,
        discount_percentage: float,
        discount_amount: float,
        expires_at: datetime,
        usage_limit: int,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.discount_percentage = discount_percentage
        self.discount_amount = discount_amount
        self.expires_at = expires_at
        self.usage_limit = usage_limit
