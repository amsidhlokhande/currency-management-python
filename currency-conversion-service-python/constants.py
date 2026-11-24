"""
Centralized Constants for Currency Conversion Service.
Loads configuration from environment variables and .env file.
"""
import os
from pathlib import Path

def _load_env_file():
    """Lightweight .env file loader ensuring zero third-party dependency issues."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v

_load_env_file()

# Service Metadata & Context Path
SERVICE_NAME: str = os.getenv("SERVICE_NAME", "currency-conversion-service-python")
PORT: int = int(os.getenv("PORT", 8100))
ENV: str = os.getenv("ENV", "development")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
CONTEXT_PATH: str = os.getenv("CONTEXT_PATH", "/currency-conversion-service-python").rstrip("/")

# Downstream Exchange Service URL (with its context path)
EXCHANGE_SERVICE_URL: str = os.getenv(
    "EXCHANGE_SERVICE_URL",
    "http://localhost:8000/currency-exchange-service-python"
).rstrip("/")

# Resiliency parameters
HTTP_TIMEOUT_CONNECT: float = float(os.getenv("HTTP_TIMEOUT_CONNECT", 1.5))
HTTP_TIMEOUT_READ: float = float(os.getenv("HTTP_TIMEOUT_READ", 3.5))
HTTP_MAX_RETRIES: int = int(os.getenv("HTTP_MAX_RETRIES", 3))
GCP_OIDC_AUTH: bool = os.getenv("GCP_OIDC_AUTH", "false").lower() in ("true", "1", "yes")

# Error Codes & Functional Error Messages (Taxonomy: CCSP)
CCSP_ERR_RATE_NOT_FOUND_CODE: str = os.getenv("CCSP_ERR_RATE_NOT_FOUND_CODE", "CCSP_001")
CCSP_ERR_RATE_NOT_FOUND_MSG: str = os.getenv(
    "CCSP_ERR_RATE_NOT_FOUND_MSG",
    "Exchange rate not available for the requested currency pair."
)

CCSP_ERR_INVALID_QUANTITY_CODE: str = os.getenv("CCSP_ERR_INVALID_QUANTITY_CODE", "CCSP_002")
CCSP_ERR_INVALID_QUANTITY_MSG: str = os.getenv(
    "CCSP_ERR_INVALID_QUANTITY_MSG",
    "Conversion quantity must be a positive numeric value greater than zero."
)

CCSP_ERR_INVALID_CURRENCY_CODE: str = os.getenv("CCSP_ERR_INVALID_CURRENCY_CODE", "CCSP_003")
CCSP_ERR_INVALID_CURRENCY_MSG: str = os.getenv(
    "CCSP_ERR_INVALID_CURRENCY_MSG",
    "Currency code must be a valid 3-letter ISO 4217 alphabetic code."
)

CCSP_ERR_DOWNSTREAM_UNAVAILABLE_CODE: str = os.getenv("CCSP_ERR_DOWNSTREAM_UNAVAILABLE_CODE", "CCSP_004")
CCSP_ERR_DOWNSTREAM_UNAVAILABLE_MSG: str = os.getenv(
    "CCSP_ERR_DOWNSTREAM_UNAVAILABLE_MSG",
    "The downstream Currency Exchange Service is currently unavailable."
)

CCSP_ERR_INTERNAL_SERVER_CODE: str = os.getenv("CCSP_ERR_INTERNAL_SERVER_CODE", "CCSP_500")
CCSP_ERR_INTERNAL_SERVER_MSG: str = os.getenv(
    "CCSP_ERR_INTERNAL_SERVER_MSG",
    "An internal processing error occurred in Currency Conversion Service."
)
