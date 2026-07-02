import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class OrderModel(Base, IdMixin):
    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    address_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("addresses.id"))
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("coupons.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_amount: Mapped[float] = mapped_column(Float)
