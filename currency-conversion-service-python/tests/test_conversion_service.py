"""
Automated Pytest Suite for Currency Conversion Service.
Tests all endpoints strictly under the /currency-conversion-service-python context path.
"""
import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
import constants
from e2e.exception.custom_exceptions import (
    ExchangeRateNotFoundException,
    ExternalServiceUnavailableException,
)

CONTEXT = constants.CONTEXT_PATH

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_conversion_success(client):
    mock_rate = {
        "id": 1001,
        "fromCurrency": "USD",
        "toCurrency": "INR",
        "conversionMultiple": 86.50,
        "environment": "currency-exchange-service-python:8000"
    }

    url = f"{CONTEXT}/currency-conversion/from/USD/to/INR/quantity/100"
    with patch("e2e.service.exchange_client.ExchangeServiceClient.get_exchange_rate", return_value=mock_rate):
        response = client.get(url)
        assert response.status_code == 200
        data = response.get_json()
        assert data["fromCurrency"] == "USD"
        assert data["toCurrency"] == "INR"
        assert data["quantity"] == 100.0
        assert data["conversionMultiple"] == 86.50
        assert data["totalCalculatedAmount"] == 8650.00
        assert data["exchangeServiceEnvironment"] == "currency-exchange-service-python:8000"
        assert "environment" in data
        assert "correlationId" in data
        assert "X-Correlation-ID" in response.headers
        assert "X-Response-Time-Ms" in response.headers


def test_conversion_invalid_currency(client):
    url = f"{CONTEXT}/currency-conversion/from/US1/to/INR/quantity/100"
    response = client.get(url)
    assert response.status_code == 400
    err = response.get_json()
    assert err["errorCode"] == "CCSP_003"
    assert "Currency code must be a valid 3-letter" in err["errorMessage"]
    assert err["path"] == url
    assert "timestamp" in err


def test_conversion_invalid_quantity(client):
    url = f"{CONTEXT}/currency-conversion/from/USD/to/INR/quantity/-50"
    response = client.get(url)
    assert response.status_code == 400
    err = response.get_json()
    assert err["errorCode"] == "CCSP_002"
    assert "Conversion quantity must be a positive" in err["errorMessage"]


def test_conversion_rate_not_found(client):
    url = f"{CONTEXT}/currency-conversion/from/USD/to/XYZ/quantity/100"
    with patch("e2e.service.exchange_client.ExchangeServiceClient.get_exchange_rate", side_effect=ExchangeRateNotFoundException("USD", "XYZ")):
        response = client.get(url)
        assert response.status_code == 404
        err = response.get_json()
        assert err["errorCode"] == "CCSP_001"
        assert "Exchange rate not available" in err["errorMessage"]


def test_conversion_downstream_failure(client):
    url = f"{CONTEXT}/currency-conversion/from/USD/to/INR/quantity/100"
    with patch("e2e.service.exchange_client.ExchangeServiceClient.get_exchange_rate", side_effect=ExternalServiceUnavailableException("exchange-service", "Connection timed out")):
        response = client.get(url)
        assert response.status_code == 503
        err = response.get_json()
        assert err["errorCode"] == "CCSP_004"
        assert "downstream Currency Exchange Service is currently unavailable" in err["errorMessage"]


def test_conversion_actuators(client):
    assert client.get(f"{CONTEXT}/health").status_code == 200
    assert client.get(f"{CONTEXT}/health/liveness").status_code == 200
    assert client.get(f"{CONTEXT}/health/readiness").status_code == 200
    assert client.get(f"{CONTEXT}/info").status_code == 200
    assert client.get(f"{CONTEXT}/metrics").status_code == 200


def test_swagger_and_openapi(client):
    res_swagger = client.get(f"{CONTEXT}/swagger")
    assert res_swagger.status_code == 200
    assert b"SwaggerUIBundle" in res_swagger.data

    res_openapi = client.get(f"{CONTEXT}/openapi.json")
    assert res_openapi.status_code == 200
    assert res_openapi.get_json()["openapi"] == "3.0.3"
