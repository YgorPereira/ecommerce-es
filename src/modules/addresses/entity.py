import uuid


class Address:
    def __init__(
        self,
        user_id: uuid.UUID,
        address_line: str,
        city: str,
        state: str,
        number: int,
        district: str,
        complement: str,
        id: uuid.UUID | None = None,
    ):
        self.id: uuid.UUID | None = id
        self.user_id = user_id
        self.address_line = address_line
        self.city = city
        self.state = state
        self.number = number
        self.district = district
        self.complement = complement
