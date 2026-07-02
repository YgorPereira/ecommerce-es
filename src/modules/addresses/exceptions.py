from src.shared.exceptions import NotFoundException


class AddressNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Endereço não encontrado")
