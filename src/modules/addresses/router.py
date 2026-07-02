from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException
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
    current_user: User = Depends(get_current_user),
):
    address.user_id = current_user.id
    return await service.create_address(address)


@address_router.get(
    "",
    response_model=List[AddressResponseSchema],
)
async def get_all_addresses(
    service: AddressService = Depends(get_address_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_addresses()


@address_router.get(
    "/{address_id}",
    response_model=AddressResponseSchema,
)
async def get_address_by_id(
    address_id: UUID,
    service: AddressService = Depends(get_address_service),
    current_user: User = Depends(get_current_user),
):
    address = await service.get_address_by_id(address_id)
    if not current_user.is_admin() and address.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return address


@address_router.get(
    "/user/{user_id}",
    response_model=List[AddressResponseSchema],
)
async def get_addresses_by_user_id(
    user_id: UUID,
    service: AddressService = Depends(get_address_service),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin() and current_user.id != user_id:
        raise UnauthorizedException("Acesso negado")
    return await service.get_addresses_by_user_id(user_id)


@address_router.put(
    "",
    response_model=AddressResponseSchema,
)
async def update_address(
    address: UpdateAddressSchema,
    service: AddressService = Depends(get_address_service),
    current_user: User = Depends(get_current_user),
):
    db_address = await service.get_address_by_id(address.id)
    if not current_user.is_admin() and db_address.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return await service.update_address(address)


@address_router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_address(
    address_id: UUID,
    service: AddressService = Depends(get_address_service),
    current_user: User = Depends(get_current_user),
):
    address = await service.get_address_by_id(address_id)
    if not current_user.is_admin() and address.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    await service.delete_address_by_id(address_id)
