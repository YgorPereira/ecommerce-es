from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.idmixin import IdMixin

if TYPE_CHECKING:
    from src.modules.products.models import ProductModel


class CategoryModel(Base, IdMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))

    products: Mapped[List["ProductModel"]] = relationship(back_populates="category")
