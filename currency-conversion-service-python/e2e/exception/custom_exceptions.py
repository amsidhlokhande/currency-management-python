"""
Custom Domain Exceptions for Currency Conversion Service.
Driven strictly by constants.py and .env error configurations.
"""
from typing import List, Optional
from enterprise_core import BaseEnterpriseException
import constants

# Backward compatibility alias
BaseCCSPException = BaseEnterpriseException


class ExchangeRateNotFoundException(BaseCCSPException):
    """Raised when the downstream exchange service does not have the conversion pair."""
    def __init__(self, from_currency: str, to_currency: str, technical_detail: str = ""):
        super().__init__(
            error_code=constants.CCSP_ERR_RATE_NOT_FOUND_CODE,
            error_message=constants.CCSP_ERR_RATE_NOT_FOUND_MSG,
            error_detail_message=technical_detail or f"Downstream rate lookup returned 404 for pair '{from_currency}' -> '{to_currency}'.",
            status_code=404,
            details=[f"No exchange rate maintained for {from_currency} -> {to_currency}."]
        )


class InvalidQuantityException(BaseCCSPException):
    """Raised when conversion quantity is negative or non-numeric."""
    def __init__(self, quantity_str: str, reason: str = ""):
        super().__init__(
            error_code=constants.CCSP_ERR_INVALID_QUANTITY_CODE,
            error_message=constants.CCSP_ERR_INVALID_QUANTITY_MSG,
            error_detail_message=reason or f"Supplied quantity value '{quantity_str}' failed positive float validation.",
            status_code=400,
            details=["Ensure quantity is a positive number (e.g. 100, 250.50)."]
        )


class InvalidCurrencyCodeException(BaseCCSPException):
    """Raised when currency code fails ISO 4217 validation."""
    def __init__(self, currency_code: str, reason: str = ""):
        super().__init__(
            error_code=constants.CCSP_ERR_INVALID_CURRENCY_CODE,
            error_message=constants.CCSP_ERR_INVALID_CURRENCY_MSG,
            error_detail_message=reason or f"Currency code '{currency_code}' does not conform to ISO 4217 format.",
            status_code=400,
            details=["Currency code must consist of exactly 3 alphabetic characters (e.g. USD, EUR, INR)."]
        )


class ExternalServiceUnavailableException(BaseCCSPException):
    """Raised when currency exchange service cannot be reached or circuit is open."""
    def __init__(self, target_service: str, technical_error: str):
        super().__init__(
            error_code=constants.CCSP_ERR_DOWNSTREAM_UNAVAILABLE_CODE,
            error_message=constants.CCSP_ERR_DOWNSTREAM_UNAVAILABLE_MSG,
            error_detail_message=f"Failed to communicate with '{target_service}': {technical_error}",
            status_code=503,
            details=["Downstream dependency is either down, timed out, or circuit breaker is OPEN. Please retry shortly."]
        )


class InternalServerException(BaseCCSPException):
    """Raised for unexpected general internal server errors."""
    def __init__(self, technical_error: str):
        super().__init__(
            error_code=constants.CCSP_ERR_INTERNAL_SERVER_CODE,
            error_message=constants.CCSP_ERR_INTERNAL_SERVER_MSG,
            error_detail_message=technical_error,
            status_code=500,
            details=["Check application system logs for detailed stack trace."]
        )
