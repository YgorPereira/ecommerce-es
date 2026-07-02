import uuid


class Category:
    def __init__(
        self,
        name: str,
        description: str,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.name = name
        self.description = description
