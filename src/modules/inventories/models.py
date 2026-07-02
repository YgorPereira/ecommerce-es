import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class InventoryModel(Base, IdMixin):
    __tablename__ = "inventories"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), unique=True, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
