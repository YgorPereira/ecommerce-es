from src.shared.exceptions import AppException, NotFoundException


class PaymentNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Pagamento não encontrado")


class PaymentGatewayException(AppException):
    def __init__(self, message: str = "Falha no gateway de pagamento"):
        super().__init__(message, status_code=502)
