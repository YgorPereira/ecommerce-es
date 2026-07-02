from typing import List
import uuid

from src.modules.addresses.entity import Address
from src.modules.addresses.exceptions import AddressNotFoundException
from src.modules.addresses.mapper import AddressMapper
from src.modules.addresses.repository import AddressRepository
from src.modules.addresses.schemas import (
    CreateAddressSchema,
    UpdateAddressSchema,
)


class AddressService:
    def __init__(self, repository: AddressRepository):
        self.repository = repository

    async def create_address(self, address: CreateAddressSchema) -> Address:
        return await self.repository.create(AddressMapper.from_create_schema(address))

    async def get_all_addresses(self) -> List[Address]:
        return await self.repository.get_all()

    async def get_address_by_id(self, id: uuid.UUID) -> Address:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise AddressNotFoundException()

        return db_item

    async def get_addresses_by_user_id(self, user_id: uuid.UUID) -> List[Address]:
        return await self.repository.get_by_user_id(user_id)

    async def update_address(self, address: UpdateAddressSchema) -> Address | None:
        db_item = await self.repository.get_by_id(address.id)

        if db_item is None:
            raise AddressNotFoundException()

        return await self.repository.update_by_id(
            Address(
                id=address.id,
                user_id=address.user_id,
                address_line=address.address_line,
                city=address.city,
                state=address.state,
                number=address.number,
                district=address.district,
                complement=address.complement,
            )
        )

    async def delete_address_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise AddressNotFoundException()

        return await self.repository.delete_by_id(id)
