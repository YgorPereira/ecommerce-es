import uuid
from datetime import datetime


class Payment:
    def __init__(
        self,
        order_id: uuid.UUID,
        amount: float,
        method: str,
        status: str,
        gateway_reference: str | None = None,
        processed_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.order_id = order_id
        self.amount = amount
        self.method = method
        self.status = status
        self.gateway_reference = gateway_reference
        self.processed_at = processed_at
