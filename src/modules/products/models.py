import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class ProductModel(Base, IdMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))