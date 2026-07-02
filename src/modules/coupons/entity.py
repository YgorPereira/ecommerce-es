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

    def is_valid(self, now: datetime) -> bool:
        """Cupom é válido se ainda tem usos e está dentro da validade."""
        return self.usage_limit > 0 and self.expires_at > now

    def apply_to(self, subtotal: float) -> float:
        """Aplica o desconto (percentual e depois valor fixo) sobre o subtotal."""
        total = subtotal - subtotal * (self.discount_percentage / 100)
        total -= self.discount_amount
        return max(total, 0.0)
