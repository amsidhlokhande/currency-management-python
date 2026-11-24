# 📋 Workflow 2: Design, Documentation & Code Implementation

## 1. Overview & Objective
Governed by **Agent 2 (Design, Docs & Implementation Engine)**. This workflow transforms the requirements into living code and publication-grade documentation. It implements the two Flask services, sets up Mermaid HLD/LLD diagrams, local setup guides, Swagger/OpenAPI docs, centralized exception handling, JSON logging with PII masking, latency interceptors, correlation ID tracing, resilience patterns, S3/local CSV loaders, and actuators.

---

## 2. Step-by-Step Execution Sequence

### Step 2.1: Microservice Structure & Scaffolding
Create clean, standard package layouts for both services:
```text
<service-dir>/
├── app/
│   ├── __init__.py           # Application factory (create_app)
│   ├── api/                  # Flask Blueprints (routes & endpoints)
│   ├── core/                 # Config, logging, interceptors, error handlers
│   ├── models/               # Domain & DTO models (Pydantic / Dataclasses)
│   ├── services/             # Business logic (rate calculation, S3/CSV loader)
│   └── client/               # Resilient HTTP client (conversion service only)
├── data/                     # Sample rate files (exchange service only)
├── tests/                    # Pytest unit & integration test suites
├── requirements.txt          # Python dependencies
├── Dockerfile                # Agent 3 collaboration
└── README.md                 # Agent 2 enriched documentation
```

### Step 2.2: Centralized Exception Handling Implementation
1. Register single point of error handling on Flask app:
   ```python
   @app.errorhandler(Exception)
   def handle_all_exceptions(e):
       ...
   ```
2. Map custom domain exceptions (`RateNotFoundException`, `ServiceUnavailableException`, `ValidationError`) into standardized JSON error responses with HTTP status codes, correlation IDs, timestamps, and error codes.

### Step 2.3: Interceptor / Filter for Millisecond Latency & PII Masked Logging
1. Register `@app.before_request`:
   - Extract or generate `X-Correlation-ID`.
   - Store start time in `g.start_time = time.perf_counter()`.
2. Register `@app.after_request`:
   - Compute `duration_ms = (time.perf_counter() - g.start_time) * 1000`.
   - Append `X-Correlation-ID` and `X-Response-Time-Ms` headers.
   - Emit single-line JSON log scrubbing all PII patterns (account numbers, emails, tokens).

### Step 2.4: Resilient Inter-Service Invocations
In `currency-conversion-service-python`:
1. Use `requests.Session` with `urllib3` retry configuration (3 attempts, backoff factor 0.5s).
2. Set strict timeouts (connect: 1s, read: 3s).
3. Circuit breaker state machine to isolate failures.
4. Propagate `X-Correlation-ID` in outgoing HTTP headers.

### Step 2.5: Ingestion of Exchange Rates (S3 / Local Windows CSV)
In `currency-exchange-service-python`:
1. Check `RATES_CSV_PATH`:
   - If `s3://<bucket>/<key>`: Stream or download via `boto3.client('s3')`.
   - If local path (e.g. `data/exchange_rates.csv` or `C:\rates\exchange_rates.csv`): Open using standard Python `csv.DictReader`.
2. Load into in-memory dictionary keyed by `(from_currency, to_currency)`.
3. Expose hot-reload endpoint: `POST /currency-exchange/reload`.

### Step 2.6: Publication-Grade `README.md` Generation
Generate modern, index-based `README.md` in each service directory containing:
- Badges and project title.
- Table of contents with anchors.
- Mermaid High-Level Design (HLD) and Sequence (LLD) diagrams.
- REST API endpoint catalog table.
- Swagger UI / OpenAPI documentation link.
- Centralized error response schema table.
- Local Windows setup & running commands.
- Actuators & health probe validation instructions.
