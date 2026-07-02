from src.shared.exceptions import ConflictException, NotFoundException


class CategoryNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Categoria não encontrada")


class CategoryNameAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("Categoria com esse nome já cadastrada")
