"""
Custom Domain Exceptions for Currency Exchange Service.
Driven strictly by constants.py and .env error configurations.
"""
from typing import List, Optional
import constants

class BaseCESPException(Exception):
    """
    Base application exception for Currency Exchange Service Python (CESP).
    Enforces unified errorCode, functional errorMessage, and technical errorDetailMessage.
    """
    def __init__(
        self,
        error_code: str,
        error_message: str,
        error_detail_message: str,
        status_code: int = 500,
        details: Optional[List[str]] = None
    ):
        super().__init__(error_message)
        self.error_code = error_code
        self.error_message = error_message
        self.error_detail_message = error_detail_message
        self.status_code = status_code
        self.details = details or []


class RateNotFoundException(BaseCESPException):
    """Raised when an exchange rate does not exist in the repository."""
    def __init__(self, from_currency: str, to_currency: str):
        super().__init__(
            error_code=constants.CESP_ERR_RATE_NOT_FOUND_CODE,
            error_message=constants.CESP_ERR_RATE_NOT_FOUND_MSG,
            error_detail_message=f"Rate lookup for conversion pair '{from_currency}' -> '{to_currency}' returned null in repository.",
            status_code=404,
            details=[f"The requested currency conversion pair {from_currency}->{to_currency} is not maintained in the active rate store."]
        )


class InvalidCurrencyCodeException(BaseCESPException):
    """Raised when an input currency code fails ISO 4217 validation."""
    def __init__(self, currency_code: str, reason: str = ""):
        technical_reason = reason or f"Currency code '{currency_code}' does not match regex ^[A-Z]{{3}}$."
        super().__init__(
            error_code=constants.CESP_ERR_INVALID_CURRENCY_CODE,
            error_message=constants.CESP_ERR_INVALID_CURRENCY_MSG,
            error_detail_message=technical_reason,
            status_code=400,
            details=["Currency code must consist of exactly 3 alphabetic characters (e.g. USD, EUR, INR)."]
        )


class DataIngestionException(BaseCESPException):
    """Raised when rate dataset loading from S3 or local CSV fails."""
    def __init__(self, source_path: str, technical_error: str):
        super().__init__(
            error_code=constants.CESP_ERR_DATA_INGESTION_CODE,
            error_message=constants.CESP_ERR_DATA_INGESTION_MSG,
            error_detail_message=f"Failed to ingest CSV data from '{source_path}': {technical_error}",
            status_code=500,
            details=[f"Ensure source file at '{source_path}' is accessible and adheres to CSV schema."]
        )


class InternalServerException(BaseCESPException):
    """Raised for general unexpected internal server errors."""
    def __init__(self, technical_error: str):
        super().__init__(
            error_code=constants.CESP_ERR_INTERNAL_SERVER_CODE,
            error_message=constants.CESP_ERR_INTERNAL_SERVER_MSG,
            error_detail_message=technical_error,
            status_code=500,
            details=["Check application system logs for detailed stack trace."]
        )
