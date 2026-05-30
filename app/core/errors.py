class AppError(Exception):
    """Base error for domain/application faults."""


class NotFoundError(AppError):
    """Raised when an entity cannot be found."""
