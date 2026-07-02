import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.idmixin import IdMixin

if TYPE_CHECKING:
    from src.modules.cart_items.models import CartItemModel
    from src.modules.coupons.models import CouponModel


class CartModel(Base, IdMixin):
    __tablename__ = "carts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("coupons.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    items: Mapped[List["CartItemModel"]] = relationship(back_populates="cart")
    coupon: Mapped["CouponModel | None"] = relationship()
