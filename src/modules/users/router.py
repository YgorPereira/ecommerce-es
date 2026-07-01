from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.users.repository import UserRepository
from src.modules.users.schemas import (
    CreateUserSchema,
    UpdateUserSchema,
    UserResponseSchema,
)
from src.modules.users.services import UserService

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


@user_router.post(
    "",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: CreateUserSchema,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user)


@user_router.get(
    "",
    response_model=List[UserResponseSchema],
)
async def get_all_users(
    service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()


@user_router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
)
async def get_user_by_id(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_id(user_id)


@user_router.get(
    "/email/{email}",
    response_model=UserResponseSchema,
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_email(email)


@user_router.put(
    "",
    response_model=UserResponseSchema,
)
async def update_user(
    user: UpdateUserSchema,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user)


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    await service.delete_user_by_id(user_id)
