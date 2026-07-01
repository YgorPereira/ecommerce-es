class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflito com recurso existente"):
        super().__init__(message, status_code=409)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, status_code=401)
