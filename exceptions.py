"""Custom exceptions for bank statement translator."""


class BankStatementError(Exception):
    """Base exception for all translator errors."""
    pass


class ValidationError(BankStatementError):
    """Raised when PDF validation fails."""
    pass


class ParseError(BankStatementError):
    """Raised when statement parsing fails."""
    pass


class TranslationError(BankStatementError):
    """Raised when translation fails."""
    pass


class OCRError(BankStatementError):
    """Raised when OCR processing fails."""
    pass


class APIError(BankStatementError):
    """Raised when API call fails."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(BankStatementError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class CacheError(BankStatementError):
    """Raised when cache operation fails."""
    pass


class ConfigurationError(BankStatementError):
    """Raised when configuration is invalid."""
    pass
