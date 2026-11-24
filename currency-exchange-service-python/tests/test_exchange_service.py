"""
Automated Pytest Suite for Currency Exchange Service.
Tests all endpoints strictly under the /currency-exchange-service-python context path.
"""
import pytest
import sys
import os

# Ensure service root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
import constants

CONTEXT = constants.CONTEXT_PATH

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_exchange_rate_success(client):
    url = f"{CONTEXT}/currency-exchange/from/USD/to/INR"
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert data["fromCurrency"] == "USD"
    assert data["toCurrency"] == "INR"
    assert data["conversionMultiple"] == 86.50
    assert "environment" in data
    # Traceability & Latency headers
    assert "X-Correlation-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_get_exchange_rate_not_found(client):
    url = f"{CONTEXT}/currency-exchange/from/USD/to/XYZ"
    response = client.get(url)
    assert response.status_code == 404
    err = response.get_json()
    assert err["errorCode"] == "CESP_001"
    assert "Exchange rate not available" in err["errorMessage"]
    assert "Rate lookup for conversion pair 'USD' -> 'XYZ'" in err["errorDetailMessage"]
    assert err["path"] == url
    assert "correlationId" in err
    assert "timestamp" in err


def test_invalid_currency_code(client):
    url = f"{CONTEXT}/currency-exchange/from/US1/to/INR"
    response = client.get(url)
    assert response.status_code == 400
    err = response.get_json()
    assert err["errorCode"] == "CESP_002"
    assert "Currency code must be a valid 3-letter" in err["errorMessage"]


def test_correlation_id_propagation(client):
    custom_id = "test-corr-trace-9999"
    url = f"{CONTEXT}/currency-exchange/from/USD/to/INR"
    response = client.get(url, headers={"X-Correlation-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_id


def test_get_all_rates(client):
    url = f"{CONTEXT}/currency-exchange/rates"
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_actuators(client):
    # Health
    res_health = client.get(f"{CONTEXT}/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "UP"

    # Liveness Probe
    res_live = client.get(f"{CONTEXT}/health/liveness")
    assert res_live.status_code == 200
    assert res_live.get_json()["status"] == "UP"

    # Readiness Probe
    res_ready = client.get(f"{CONTEXT}/health/readiness")
    assert res_ready.status_code == 200
    assert res_ready.get_json()["status"] == "UP"

    # Info
    res_info = client.get(f"{CONTEXT}/info")
    assert res_info.status_code == 200
    assert res_info.get_json()["app"]["contextPath"] == CONTEXT

    # Metrics
    res_metrics = client.get(f"{CONTEXT}/metrics")
    assert res_metrics.status_code == 200


def test_swagger_and_openapi(client):
    res_swagger = client.get(f"{CONTEXT}/swagger")
    assert res_swagger.status_code == 200
    assert b"SwaggerUIBundle" in res_swagger.data

    res_openapi = client.get(f"{CONTEXT}/openapi.json")
    assert res_openapi.status_code == 200
    assert res_openapi.get_json()["openapi"] == "3.0.3"


def test_reload_rates(client):
    res_reload = client.post(f"{CONTEXT}/currency-exchange/reload")
    assert res_reload.status_code == 200
    data = res_reload.get_json()
    assert data["totalPairs"] > 0
