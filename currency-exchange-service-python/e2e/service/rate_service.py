"""
Core Business Service for Currency Exchange Rates.
Dual-mode Ingestion: AWS S3 vs Local Windows File (C:\\rates\\exchange_rates.csv).
"""
import csv
import io
import os
import logging
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, List, Tuple
import constants
from e2e.modules.exchange_rate import ExchangeRate
from e2e.exception.custom_exceptions import (
    RateNotFoundException,
    InvalidCurrencyCodeException,
    DataIngestionException,
)

logger = logging.getLogger(__name__)

class RateService:
    """Thread-safe in-memory currency exchange rate authority."""
    def __init__(self):
        self._lock = threading.RLock()
        self._rates: Dict[Tuple[str, str], ExchangeRate] = {}
        self.data_source = ""
        self.environment_id = f"{constants.SERVICE_NAME}:{constants.PORT}"

    def load_rates(self):
        """Loads exchange rate dataset from S3 or local Windows filesystem."""
        with self._lock:
            path = constants.RATES_CSV_PATH
            logger.info(f"Initiating currency exchange rates load from: {path}")

            if path.startswith("s3://"):
                csv_content = self._load_from_s3(path)
                self.data_source = f"AWS S3 [{path}]"
            else:
                csv_content = self._load_from_local_file(path)
                self.data_source = f"Local File [{path}]"

            self._rates = self._parse_csv_content(csv_content)
            logger.info(f"Successfully loaded {len(self._rates)} currency exchange pairs into memory.")

    def _load_from_local_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            # Check fallback bundled file if primary path not found
            fallback = os.path.join(os.path.dirname(__file__), "..", "..", "data", "exchange_rates.csv")
            fallback = os.path.abspath(fallback)
            if os.path.exists(fallback):
                logger.warning(f"Configured path '{file_path}' not found. Falling back to bundled CSV: {fallback}")
                file_path = fallback
            else:
                raise DataIngestionException(file_path, f"File does not exist at '{file_path}' or fallback '{fallback}'.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise DataIngestionException(file_path, str(e))

    def _load_from_s3(self, s3_uri: str) -> str:
        try:
            import boto3
            parsed = urlparse(s3_uri)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")

            s3_client = boto3.client(
                "s3",
                region_name=constants.AWS_REGION,
                aws_access_key_id=constants.AWS_ACCESS_KEY_ID or None,
                aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY or None
            )
            response = s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read().decode("utf-8")
        except Exception as e:
            logger.error(f"S3 ingestion error for URI '{s3_uri}': {str(e)}")
            raise DataIngestionException(s3_uri, str(e))

    def _parse_csv_content(self, content: str) -> Dict[Tuple[str, str], ExchangeRate]:
        rates_map = {}
        reader = csv.DictReader(io.StringIO(content))
        auto_id = 1000
        now_iso = datetime.now(timezone.utc).isoformat()

        for idx, row in enumerate(reader, start=1):
            from_curr = (row.get("fromCurrency") or row.get("from_currency") or row.get("from") or "").strip().upper()
            to_curr = (row.get("toCurrency") or row.get("to_currency") or row.get("to") or "").strip().upper()
            raw_rate = row.get("Rate") or row.get("rate") or row.get("conversionMultiple") or row.get("conversion_multiple")

            if not from_curr or not to_curr or raw_rate is None:
                continue

            try:
                rate_val = float(raw_rate)
            except ValueError:
                continue

            rate_id = int(row.get("id", auto_id + idx))
            rate_obj = ExchangeRate(
                id=rate_id,
                fromCurrency=from_curr,
                toCurrency=to_curr,
                conversionMultiple=rate_val,
                environment=self.environment_id,
                lastUpdated=now_iso
            )
            rates_map[(from_curr, to_curr)] = rate_obj

        return rates_map

    def get_rate(self, from_currency: str, to_currency: str) -> ExchangeRate:
        """Retrieves conversion multiple for currency pair with validation."""
        try:
            from_valid = ExchangeRate.validate_currency_code(from_currency)
        except ValueError as e:
            raise InvalidCurrencyCodeException(from_currency, str(e))

        try:
            to_valid = ExchangeRate.validate_currency_code(to_currency)
        except ValueError as e:
            raise InvalidCurrencyCodeException(to_currency, str(e))

        with self._lock:
            key = (from_valid, to_valid)
            if key in self._rates:
                return self._rates[key]
            
            # Identity rate (e.g. USD to USD = 1.0)
            if from_valid == to_valid:
                return ExchangeRate(
                    id=9999,
                    fromCurrency=from_valid,
                    toCurrency=to_valid,
                    conversionMultiple=1.0,
                    environment=self.environment_id,
                    lastUpdated=datetime.now(timezone.utc).isoformat()
                )

            raise RateNotFoundException(from_valid, to_valid)

    def get_all_rates(self) -> List[ExchangeRate]:
        """Returns all currently maintained rates."""
        with self._lock:
            return list(self._rates.values())

    def reload(self) -> int:
        """Hot-reloads rates into memory."""
        self.load_rates()
        return len(self._rates)


rate_service = RateService()
