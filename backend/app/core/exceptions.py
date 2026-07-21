class DomainException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundException(DomainException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ForbiddenException(DomainException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class ConflictException(DomainException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message)


class BadRequestException(DomainException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message)


class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message)
