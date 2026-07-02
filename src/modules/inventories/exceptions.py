from src.shared.exceptions import ConflictException, NotFoundException


class InventoryNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Estoque não encontrado")


class InventoryAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("Estoque já cadastrado para esse produto")


class InsufficientStockException(ConflictException):
    def __init__(self):
        super().__init__("Estoque insuficiente para o produto")
