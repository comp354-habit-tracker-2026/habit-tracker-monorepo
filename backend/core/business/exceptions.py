class DomainValidationError(ValueError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code
