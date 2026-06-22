"""Custom error types and exceptions for MailAuthCheck."""
from __future__ import annotations

from enum import Enum
from fastapi import status


class ErrorCode(str, Enum):
    """Error codes returned in API responses."""
    INVALID_DOMAIN = "invalid_domain"
    DNS_TIMEOUT = "dns_timeout"
    DNS_ERROR = "dns_error"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"
    VALIDATION_ERROR = "validation_error"


class MailAuthCheckError(Exception):
    """Base exception for MailAuthCheck errors."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(self.message)


class InvalidDomainError(MailAuthCheckError):
    """Raised when domain input is invalid."""

    def __init__(self, message: str):
        super().__init__(
            code=ErrorCode.INVALID_DOMAIN,
            message=message,
            http_status=status.HTTP_400_BAD_REQUEST,
        )


class DNSTimeoutError(MailAuthCheckError):
    """Raised when DNS query times out."""

    def __init__(self, domain: str = ""):
        super().__init__(
            code=ErrorCode.DNS_TIMEOUT,
            message="DNS query timeout. Please try again.",
            http_status=status.HTTP_408_REQUEST_TIMEOUT,
            details={"domain": domain} if domain else {},
        )


class DNSError(MailAuthCheckError):
    """Raised when DNS query fails."""

    def __init__(self, message: str, domain: str = ""):
        super().__init__(
            code=ErrorCode.DNS_ERROR,
            message=message,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"domain": domain} if domain else {},
        )


class RateLimitError(MailAuthCheckError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            code=ErrorCode.RATE_LIMITED,
            message="Too many requests. Please wait before trying again.",
            http_status=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )
