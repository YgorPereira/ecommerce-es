from src.modules.users.enums.role import UserRole


class User:
    def __init__(self, name: str, cpf: str, email: str, role: UserRole):
        self.name = name
        self.cpf = cpf
        self.email = email
        self.role = role

    def is_admin(self):
        return self.role == UserRole.ADMIN
