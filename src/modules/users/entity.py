
from src.modules.users.enums.role import UserRole


class User:
    def __init__(self, id: uuid.UUID, name: str, cpf: str, email: str, role: UserRole, password: str):
        self.id = id
        self.name = name
        self.cpf = cpf
        self.email = email
        self.role = role
        self.password = password


    def is_admin(self):
        return self.role == UserRole.ADMIN

