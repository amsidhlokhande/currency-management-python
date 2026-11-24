"""
Currency Conversion Business Service.
Orchestrates rate query, quantity validation, and precision calculation.
"""
from datetime import datetime, timezone
from flask import g
import constants
from e2e.modules.conversion_result import ConversionResult
from e2e.service.exchange_client import exchange_client
from e2e.exception.custom_exceptions import (
    InvalidCurrencyCodeException,
    InvalidQuantityException,
)

class ConversionService:
    def __init__(self):
        self.environment = f"{constants.SERVICE_NAME}:{constants.PORT}"

    def calculate_conversion(self, from_curr: str, to_curr: str, quantity_str: str) -> ConversionResult:
        """Validates inputs, retrieves live rate, and computes total amount."""
        try:
            valid_from = ConversionResult.validate_currency(from_curr)
        except ValueError as e:
            raise InvalidCurrencyCodeException(from_curr, str(e))

        try:
            valid_to = ConversionResult.validate_currency(to_curr)
        except ValueError as e:
            raise InvalidCurrencyCodeException(to_curr, str(e))

        try:
            valid_qty = ConversionResult.validate_quantity(quantity_str)
        except ValueError as e:
            raise InvalidQuantityException(quantity_str, str(e))

        # Delegate to exchange service
        rate_dto = exchange_client.get_exchange_rate(valid_from, valid_to)
        
        conversion_multiple = float(rate_dto.get("conversionMultiple", 0.0))
        exchange_env = rate_dto.get("environment", "UNKNOWN_EXCHANGE_HOST")
        rate_id = int(rate_dto.get("id", 2000))

        # Precision calculation
        total_amount = round(valid_qty * conversion_multiple, 4)
        correlation_id = getattr(g, "correlation_id", "NO_CORRELATION_ID")

        return ConversionResult(
            id=rate_id,
            fromCurrency=valid_from,
            toCurrency=valid_to,
            conversionMultiple=conversion_multiple,
            quantity=valid_qty,
            totalCalculatedAmount=total_amount,
            environment=self.environment,
            exchangeServiceEnvironment=exchange_env,
            correlationId=correlation_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )


conversion_service = ConversionService()
