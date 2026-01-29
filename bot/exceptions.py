class BotError(Exception):
    """Base exception for the trading bot."""


class ValidationError(BotError):
    """Raised when CLI/user input validation fails."""


class ApiError(BotError):
    """Raised for Binance API errors (HTTP errors or error JSON)."""

    def __init__(self, message: str, status_code: int | None = None, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class NetworkError(BotError):
    """Raised for network/timeout issues."""
