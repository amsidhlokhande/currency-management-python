"""
JSON Logging Utility for Currency Conversion Service.
Delegates to the shared enterprise_core logging engine with automatic PII masking.
"""
from enterprise_core import (
    setup_enterprise_logging,
    PIIMaskingFilter,
    JsonLogFormatter
)
import constants

def configure_logging(log_level: str = "INFO"):
    """Configures structured JSON logging with PII masking via enterprise_core."""
    setup_enterprise_logging(
        service_name=constants.SERVICE_NAME,
        log_level=log_level
    )

__all__ = ["configure_logging", "PIIMaskingFilter", "JsonLogFormatter"]
