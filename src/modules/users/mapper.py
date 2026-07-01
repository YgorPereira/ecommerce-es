from src.modules.users.entity import User
from src.modules.users.models import UserModel
from src.modules.users.schemas import CreateUserSchema, UpdateUserSchema


class UserMapper():
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            name=entity.name,
            cpf=entity.cpf,
            email=entity.email,
            password=entity.password,
            role=entity.role,
        )

    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            cpf=model.cpf,
            email=model.email,
            password=model.password,
            role=model.role,
        )
    
    @staticmethod
    def from_create_schema(schema: CreateUserSchema) -> User:
        return User(
            name=schema.name,
            cpf=schema.cpf,
            email=schema.email,
            password=schema.password,
            role=schema.role,
        )