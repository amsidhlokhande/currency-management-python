"""
Currency Conversion Result Domain Model and DTOs.
"""
import re
from dataclasses import dataclass, asdict
from typing import Dict, Any

CURRENCY_PATTERN = re.compile(r'^[A-Z]{3}$')

@dataclass
class ConversionResult:
    """
    Core Domain Model representing a completed financial currency conversion calculation.
    """
    id: int
    fromCurrency: str
    toCurrency: str
    conversionMultiple: float
    quantity: float
    totalCalculatedAmount: float
    environment: str
    exchangeServiceEnvironment: str
    correlationId: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert domain model to JSON-serializable dictionary."""
        return asdict(self)

    @staticmethod
    def validate_currency(code: str) -> str:
        """Validates ISO 4217 standard 3-letter currency code."""
        if not code or not isinstance(code, str):
            raise ValueError(f"Currency code must be non-empty string, got '{code}'")
        code_upper = code.strip().upper()
        if not CURRENCY_PATTERN.match(code_upper):
            raise ValueError(f"Invalid currency code format '{code}'. Must be 3 alphabetic letters.")
        return code_upper

    @staticmethod
    def validate_quantity(qty_str: str) -> float:
        """Validates that quantity is a positive float."""
        try:
            qty = float(qty_str)
            if qty <= 0:
                raise ValueError(f"Quantity must be greater than zero, got '{qty_str}'")
            return qty
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric quantity '{qty_str}': {str(e)}")
