"""
Centralized Constants for Currency Exchange Service.
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
SERVICE_NAME: str = os.getenv("SERVICE_NAME", "currency-exchange-service-python")
PORT: int = int(os.getenv("PORT", 8000))
ENV: str = os.getenv("ENV", "development")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
CONTEXT_PATH: str = os.getenv("CONTEXT_PATH", "/currency-exchange-service-python").rstrip("/")

# Rate Ingestion Configuration (Dual Mode)
_default_csv = r"C:\rates\exchange_rates.csv" if os.name == "nt" and os.path.exists(r"C:\rates\exchange_rates.csv") else str(Path(__file__).resolve().parent / "data" / "exchange_rates.csv")
RATES_CSV_PATH: str = os.getenv("RATES_CSV_PATH", _default_csv)

# AWS Credentials (optional for S3 mode)
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Error Codes & Functional Error Messages (Taxonomy: CESP)
CESP_ERR_RATE_NOT_FOUND_CODE: str = os.getenv("CESP_ERR_RATE_NOT_FOUND_CODE", "CESP_001")
CESP_ERR_RATE_NOT_FOUND_MSG: str = os.getenv(
    "CESP_ERR_RATE_NOT_FOUND_MSG",
    "Exchange rate not available for the requested currency pair."
)

CESP_ERR_INVALID_CURRENCY_CODE: str = os.getenv("CESP_ERR_INVALID_CURRENCY_CODE", "CESP_002")
CESP_ERR_INVALID_CURRENCY_MSG: str = os.getenv(
    "CESP_ERR_INVALID_CURRENCY_MSG",
    "Currency code must be a valid 3-letter ISO 4217 alphabetic code."
)

CESP_ERR_DATA_INGESTION_CODE: str = os.getenv("CESP_ERR_DATA_INGESTION_CODE", "CESP_003")
CESP_ERR_DATA_INGESTION_MSG: str = os.getenv(
    "CESP_ERR_DATA_INGESTION_MSG",
    "Unable to load currency exchange rate dataset from configured source."
)

CESP_ERR_INTERNAL_SERVER_CODE: str = os.getenv("CESP_ERR_INTERNAL_SERVER_CODE", "CESP_500")
CESP_ERR_INTERNAL_SERVER_MSG: str = os.getenv(
    "CESP_ERR_INTERNAL_SERVER_MSG",
    "An internal processing error occurred in Currency Exchange Service."
)
