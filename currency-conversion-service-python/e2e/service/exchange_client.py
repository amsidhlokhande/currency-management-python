"""
Resilient HTTP Client communicating with currency-exchange-service-python.
Features:
- Retries with exponential backoff
- Configurable Connect/Read Timeouts
- Circuit Breaker pattern
- Correlation ID propagation
- Optional Google IAM OIDC token injection for Cloud Run
"""
import time
import logging
from typing import Dict, Any
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from flask import g
import constants
from e2e.exception.custom_exceptions import (
    ExternalServiceUnavailableException,
    ExchangeRateNotFoundException,
)

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Lightweight resilient circuit breaker to prevent cascading failures.
    Transitions: CLOSED -> OPEN (on 5 failures) -> HALF_OPEN (after cooldown).
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 15.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_state_change = time.time()

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if (time.time() - self.last_state_change) > self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.last_state_change = time.time()
                logger.info("Circuit breaker transitioned to HALF_OPEN probe state.")
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info("Circuit breaker recovered. Transitioning to CLOSED.")
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            logger.error(f"Circuit breaker tripped OPEN! Consecutive failures: {self.failure_count}")


class ExchangeServiceClient:
    """
    Client for invoking currency-exchange-service-python.
    """
    def __init__(self):
        self.base_url = constants.EXCHANGE_SERVICE_URL
        self.circuit_breaker = CircuitBreaker()
        self.session = requests.Session()

        # Exponential backoff retries
        retries = Retry(
            total=constants.HTTP_MAX_RETRIES,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_gcp_oidc_token(self, audience: str) -> str:
        """Fetch OIDC identity token from GCP metadata server when running in Cloud Run."""
        if not constants.GCP_OIDC_AUTH:
            return ""
        try:
            metadata_url = f"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience={audience}"
            headers = {"Metadata-Flavor": "Google"}
            resp = requests.get(metadata_url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception as e:
            logger.warning(f"Could not retrieve GCP OIDC token: {str(e)}")
        return ""

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Fetches live exchange rate entity from currency-exchange-service-python."""
        if not self.circuit_breaker.can_execute():
            raise ExternalServiceUnavailableException(
                "currency-exchange-service-python",
                "Circuit breaker is OPEN due to repeated downstream failures."
            )

        endpoint = f"{self.base_url}/currency-exchange/from/{from_currency}/to/{to_currency}"
        correlation_id = getattr(g, "correlation_id", "NO_CORRELATION_ID")
        headers = {
            "Accept": "application/json",
            "X-Correlation-ID": correlation_id
        }

        oidc_token = self._get_gcp_oidc_token(self.base_url)
        if oidc_token:
            headers["Authorization"] = f"Bearer {oidc_token}"

        timeout = (constants.HTTP_TIMEOUT_CONNECT, constants.HTTP_TIMEOUT_READ)
        logger.info(f"Invoking Exchange Service: {endpoint} [Correlation: {correlation_id}]")

        try:
            response = self.session.get(endpoint, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                self.circuit_breaker.record_success()
                return response.json()
            elif response.status_code == 404:
                raise ExchangeRateNotFoundException(
                    from_currency,
                    to_currency,
                    f"Exchange service responded 404: {response.text}"
                )
            else:
                self.circuit_breaker.record_failure()
                raise ExternalServiceUnavailableException(
                    "currency-exchange-service-python",
                    f"Exchange service returned HTTP {response.status_code}: {response.text}"
                )

        except (requests.ConnectionError, requests.Timeout) as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Exchange service connection failure: {str(e)}")
            raise ExternalServiceUnavailableException(
                "currency-exchange-service-python",
                f"Connection error reaching {self.base_url}: {str(e)}"
            )


exchange_client = ExchangeServiceClient()
