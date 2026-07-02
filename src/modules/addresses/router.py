from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.addresses.repository import AddressRepository
from src.modules.addresses.schemas import (
    CreateAddressSchema,
    UpdateAddressSchema,
    AddressResponseSchema,
)
from src.modules.addresses.services import AddressService

address_router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


def get_address_service(
    db: Session = Depends(get_db),
) -> AddressService:
    repository = AddressRepository(db)
    return AddressService(repository)


@address_router.post(
    "",
    response_model=AddressResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    address: CreateAddressSchema,
    service: AddressService = Depends(get_address_service),
):
    return await service.create_address(address)


@address_router.get(
    "",
    response_model=List[AddressResponseSchema],
)
async def get_all_addresses(
    service: AddressService = Depends(get_address_service),
):
    return await service.get_all_addresses()


@address_router.get(
    "/{address_id}",
    response_model=AddressResponseSchema,
)
async def get_address_by_id(
    address_id: UUID,
    service: AddressService = Depends(get_address_service),
):
    return await service.get_address_by_id(address_id)


@address_router.get(
    "/user/{user_id}",
    response_model=List[AddressResponseSchema],
)
async def get_addresses_by_user_id(
    user_id: UUID,
    service: AddressService = Depends(get_address_service),
):
    return await service.get_addresses_by_user_id(user_id)


@address_router.put(
    "",
    response_model=AddressResponseSchema,
)
async def update_address(
    address: UpdateAddressSchema,
    service: AddressService = Depends(get_address_service),
):
    return await service.update_address(address)


@address_router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_address(
    address_id: UUID,
    service: AddressService = Depends(get_address_service),
):
    await service.delete_address_by_id(address_id)
