import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class CartModel(Base, IdMixin):
    __tablename__ = "carts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("coupons.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
