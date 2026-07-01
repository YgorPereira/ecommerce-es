from src.shared.exceptions import ConflictException, NotFoundException


class ProductNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Produto não encontrado")


class ProductNameAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("Produto com esse nome já cadastrado")