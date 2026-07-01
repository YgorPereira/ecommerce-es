import uuid


class Product:
    def __init__(
        self,
        name: str,
        price: float,
        description: str,
        category_id: uuid.UUID,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.name = name
        self.price = price
        self.description = description
        self.category_id = category_id