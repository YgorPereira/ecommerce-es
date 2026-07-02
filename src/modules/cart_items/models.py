import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.idmixin import IdMixin

if TYPE_CHECKING:
    from src.modules.carts.models import CartModel
    from src.modules.products.models import ProductModel


class CartItemModel(Base, IdMixin):
    __tablename__ = "cart_items"

    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    cart: Mapped["CartModel"] = relationship(back_populates="items")
    product: Mapped["ProductModel"] = relationship()
