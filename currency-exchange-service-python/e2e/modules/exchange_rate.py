"""
Exchange Rate Domain Model and DTOs.
"""
import re
from dataclasses import dataclass, asdict
from typing import Dict, Any

CURRENCY_PATTERN = re.compile(r'^[A-Z]{3}$')

@dataclass
class ExchangeRate:
    """
    Core Domain Model representing an authoritative currency exchange rate.
    """
    id: int
    fromCurrency: str
    toCurrency: str
    conversionMultiple: float
    environment: str
    lastUpdated: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert domain model to JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def validate_currency_code(cls, code: str) -> str:
        """
        Validates ISO 4217 standard 3-letter currency code.
        Returns uppercase validated string or raises ValueError.
        """
        if not code or not isinstance(code, str):
            raise ValueError(f"Currency code must be non-empty string, got '{code}'")
        code_upper = code.strip().upper()
        if not CURRENCY_PATTERN.match(code_upper):
            raise ValueError(f"Invalid currency code format '{code}'. Must be 3 alphabetic letters.")
        return code_upper
