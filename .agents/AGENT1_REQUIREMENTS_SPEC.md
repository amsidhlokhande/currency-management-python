# 🏛️ Agent 1: Requirements & Architecture Specification Playbook

## 1. Agent Persona & Mandate

- **Role**: Principal Cloud & Systems Architect (Requirements & Architecture Specialist)
- **Primary Mission**: Author, maintain, and continuously synchronize the comprehensive Project Requirements Document (PRD), architectural specifications, domain models, and technical stack standards across the dual Python/Flask microservices ecosystem.
- **Monitoring & Sync Mandate**: Constantly inspect the codebase, Dockerfiles, and deployment manifests produced by Agent 2, Agent 3, and Agent 4. Automatically reconcile and update requirements whenever design or implementation changes occur.

---

## 2. Technical Stack Specification

| Component | Standard / Library | Justification & Version |
| :--- | :--- | :--- |
| **Language Runtime** | **Python 3.15.2** | Modern Python runtime leveraging performance enhancements, freethreaded/standard compatibility, and modern typing. |
| **Web Framework** | **Flask 3.1.x** | Lightweight, production-proven microservice web framework with modular Blueprints and robust WSGI ecosystem. |
| **WSGI Server** | **Gunicorn 23.x** (Linux/Docker) / **Waitress** (Windows) | High-concurrency production-grade WSGI HTTP server with pre-fork worker model and tunable worker threads. |
| **Configuration & Secrets** | **python-dotenv / os.environ** | Layered configuration loading from `.env` files with OS environment overrides. |
| **Data Validation & Schemas** | **Pydantic v2 / Marshmallow / Dataclasses** | High-performance type validation, schema serialization, and strict input/output verification. |
| **HTTP Client & Resilience** | **Requests + urllib3 Retry / CircuitBreaker** | Resilient client for inter-service communication with exponential backoff, jitter, timeouts, and circuit-breaker patterns. |
| **Cloud Storage Client** | **Boto3 / botocore** | Enterprise AWS S3 client with local Windows file fallback for loading CSV rate datasets. |
| **Structured Logging** | **python-json-logger** | Zero-leakage JSON structured logging equipped with automatic PII masking and MDC context. |
| **API Documentation** | **OpenAPI 3.0 / Swagger UI** | Swagger UI and OpenAPI 3.0 specification auto-rendered at `/swagger` under the service context path. |
| **Testing Harness** | **Pytest, unittest.mock** | Automated unit and integration testing suite enforcing >= 85% branch coverage. |

---

## 3. Microservice Specifications & Context Paths

### 3.1 Service Context Paths Standards
Every microservice must expose ALL routes (business endpoints, actuator health probes, metrics, and Swagger/OpenAPI documentation) under a dedicated base context path:
- **`currency-exchange-service-python` Context Path**: `/currency-exchange-service-python`
- **`currency-conversion-service-python` Context Path**: `/currency-conversion-service-python`

---

### 3.2 Service 1: `currency-exchange-service-python`

#### Purpose & Bounded Context:
Acts as the central authority for currency conversion rates. Ingests rate sheets from external S3 buckets or local file systems and serves them via high-performance REST APIs.

#### Standard Context Path:
`/currency-exchange-service-python`

#### Functional Requirements (FR):
- **FR-EX-01 (Rate Ingestion - Dual Mode Environment-Driven)**:
  - **Local Windows Machine**: Reads rate dataset directly from `RATES_CSV_PATH="C:\rates\exchange_rates.csv"` (with bundled relative fallback `data/exchange_rates.csv`).
  - **Cloud Run / Production Environment**: Reads dynamically from `s3://` URI specified in `RATES_CSV_PATH` (e.g. `s3://currency-rates-bucket/exchange_rates.csv`) using `boto3`.
  - **Dataset Columns**: Strict adherence to CSV schema: `fromCurrency,toCurrency,Rate`. In-memory model maps `Rate` to `conversionMultiple`.
- **FR-EX-02 (Rate Lookup Endpoint)**: Expose `GET /currency-exchange-service-python/currency-exchange/from/{from}/to/{to}` returning the exchange rate entity.
- **FR-EX-03 (All Rates Endpoint)**: Expose `GET /currency-exchange-service-python/currency-exchange/rates` to retrieve the entire catalog of supported currency pairs.
- **FR-EX-04 (Cache & Reload)**: Support in-memory caching with a hot-reload endpoint `POST /currency-exchange-service-python/currency-exchange/reload` for zero-downtime rate refreshes.
- **FR-EX-05 (Actuators & Probes)**: Provide `/currency-exchange-service-python/health`, `/currency-exchange-service-python/health/liveness`, `/currency-exchange-service-python/health/readiness`, `/currency-exchange-service-python/info`, and `/currency-exchange-service-python/metrics`.
- **FR-EX-06 (Centralized Error Handling)**: Standard error envelope returning unified error template driven by `.env` and `constants.py` with `CESP_` prefix (e.g. `CESP_001`).

#### Error Codes & Messages Taxonomy (`CESP`):
- `CESP_ERR_RATE_NOT_FOUND_CODE=CESP_001`: Exchange rate not available for requested pair
- `CESP_ERR_INVALID_CURRENCY_CODE=CESP_002`: Invalid 3-letter ISO 4217 currency code
- `CESP_ERR_DATA_INGESTION_CODE=CESP_003`: Unable to load exchange rate dataset
- `CESP_ERR_INTERNAL_SERVER_CODE=CESP_500`: Internal processing error in exchange service

---

### 3.3 Service 2: `currency-conversion-service-python`

#### Purpose & Bounded Context:
Orchestrates currency calculation by delegating rate queries to `currency-exchange-service-python`, multiplying the conversion multiple by the requested quantity, and providing a comprehensive financial conversion record.

#### Standard Context Path:
`/currency-conversion-service-python`

#### Functional Requirements (FR):
- **FR-CV-01 (Calculation Endpoint)**: Expose `GET /currency-conversion-service-python/currency-conversion/from/{from}/to/{to}/quantity/{quantity}`.
- **FR-CV-02 (Inter-Service Delegation)**: Issue resilient HTTP `GET` request to `currency-exchange-service-python` at `/currency-exchange-service-python/currency-exchange/from/{from}/to/{to}`.
- **FR-CV-03 (Computation Engine)**: Total Amount = `quantity * conversionMultiple` computed with decimal precision.
- **FR-CV-04 (Traceability)**: Accept `X-Correlation-ID` header from client or generate UUIDv4 if missing, propagating it downstream to `currency-exchange-service-python`.
- **FR-CV-05 (Fault Tolerance & Resilience)**: Retry up to 3 times with exponential backoff and circuit-breaker tripping upon consecutive failures.
- **FR-CV-06 (Actuators & Probes)**: Expose `/currency-conversion-service-python/health`, `/currency-conversion-service-python/health/liveness`, `/currency-conversion-service-python/health/readiness`, `/currency-conversion-service-python/info`, and `/currency-conversion-service-python/metrics`.

#### Error Codes & Messages Taxonomy (`CCSP`):
- `CCSP_ERR_RATE_NOT_FOUND_CODE=CCSP_001`: Exchange rate not available for requested pair
- `CCSP_ERR_INVALID_QUANTITY_CODE=CCSP_002`: Invalid monetary quantity specified
- `CCSP_ERR_INVALID_CURRENCY_CODE=CCSP_003`: Invalid 3-letter ISO 4217 currency code
- `CCSP_ERR_DOWNSTREAM_UNAVAILABLE_CODE=CCSP_004`: Downstream exchange service is unavailable
- `CCSP_ERR_INTERNAL_SERVER_CODE=CCSP_500`: Internal processing error in conversion service

---

### 3.4 Common Generic Error Response Specification
Every error across both services MUST conform strictly to this unified JSON structure:
```json
{
  "timestamp": "2026-11-24T02:08:00.123456Z",
  "status": 404,
  "errorCode": "CESP_001",
  "errorMessage": "Exchange rate not available for the requested currency pair",
  "errorDetailMessage": "Rate lookup for currency pair 'USD' -> 'XYZ' returned null in repository",
  "path": "/currency-exchange-service-python/currency-exchange/from/USD/to/XYZ",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "details": [
    "Ensure both fromCurrency and toCurrency exist in the rate dataset."
  ]
}
```

---

### 3.5 Layered Project Architecture Standard
Both services adhere strictly to the following standardized modular structure:
```text
<service-directory>/
├── .env                  # Environment variables & error code configurations
├── app.py                # Main application bootstrap & WSGI runner
├── constants.py          # Centralized constants (.env values, error mappings)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Multi-stage production container definition
├── README.md             # Publication-grade Mermaid architecture docs
├── data/                 # Sample data files (rates CSV)
├── tests/                # Automated pytest unit & integration test suite
└── e2e/                  # End-to-End Enterprise Architecture Package
    ├── __init__.py
    ├── config/           # Application configuration loader
    ├── route/            # HTTP routes, actuators & Swagger UI under context path
    ├── modules/          # Data models, DTOs & request/response schemas
    ├── service/          # Core business logic & resilient HTTP client
    ├── exception/        # Custom domain exceptions & centralized error handler
    └── utils/            # JSON logger with PII masking, latency interceptors
```
