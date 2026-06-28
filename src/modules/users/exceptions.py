

from src.shared.exceptions import ConflictException, NotFoundException


class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Usuário não encontrado")


class UserEmailAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("E-mail já cadastrado")


class UserCpfAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("CPF já cadastrado")