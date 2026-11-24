# 📘 Approach 2: Shared Internal Enterprise Library (`enterprise-core-python`)

> **Branch**: `shared-enterprise-library`  
> **Target Audience**: Enterprise Architects, Platform Engineers, Tech Leads, and Backend Developers  
> **Java Analogy**: Custom Spring Boot Starter (e.g., `company-spring-boot-starter-web`) providing both dependency versions and foundational cross-cutting components.

---

## 📑 Table of Contents
1. [Problem Statement & Enterprise Motivation](#1-problem-statement--enterprise-motivation)
2. [Architectural Concept & Comparison to Spring Boot Starter](#2-architectural-concept--comparison-to-spring-boot-starter)
3. [Anatomy of `enterprise-core-python`](#3-anatomy-of-enterprise-core-python)
   - [3.1 Structured Logging & PII Masking](#31-structured-logging--pii-masking)
   - [3.2 Enterprise Error Handling & Unified JSON Envelope](#32-enterprise-error-handling--unified-json-envelope)
   - [3.3 Latency & Correlation ID Interceptors](#33-latency--correlation-id-interceptors)
   - [3.4 Spring Boot-Style Actuator Health & Metrics Probes](#34-spring-boot-style-actuator-health--metrics-probes)
   - [3.5 Reusable OpenAPI 3.0 & Swagger UI Blueprint](#35-reusable-openapi-30--swagger-ui-blueprint)
4. [Step-by-Step Implementation Guide](#4-step-by-step-implementation-guide)
   - [Step 4.1: Inspect the Library Structure & Dependencies (`setup.py`)](#step-41-inspect-the-library-structure--dependencies-setuppy)
   - [Step 4.2: Build the Wheel Distribution](#step-42-build-the-wheel-distribution)
   - [Step 4.3: Publishing to Internal Artifact Registries (Artifactory, Nexus, AWS, GCP)](#step-43-publishing-to-internal-artifact-registries-artifactory-nexus-aws-gcp)
   - [Step 4.4: Refactor Microservices to Consume `enterprise-core-python`](#step-44-refactor-microservices-to-consume-enterprise-core-python)
   - [Step 4.5: Bootstrap Enterprise Core in Microservice `app.py`](#step-45-bootstrap-enterprise-core-in-microservice-apppy)
5. [Local Development & Verification](#5-local-development--verification)
   - [Editable Install Mode](#editable-install-mode)
   - [Running Library and Microservice Tests](#running-library-and-microservice-tests)
6. [Containerization & Docker Build Pipeline](#6-containerization--docker-build-pipeline)
   - [Consuming Wheels Locally in Docker](#consuming-wheels-locally-in-docker)
   - [Consuming Wheels from Private Artifactory / PyPI in Docker](#consuming-wheels-from-private-artifactory--pypi-in-docker)
   - [Docker Compose Smoke Testing](#docker-compose-smoke-testing)
7. [How to Patch a Security Vulnerability (CVE) in Seconds](#7-how-to-patch-a-security-vulnerability-cve-in-seconds)
8. [CLI Command Reference & Cheat Sheet](#8-cli-command-reference--cheat-sheet)

---

## 1. Problem Statement & Enterprise Motivation

When managing **36+ Python microservices**, two major problems compound each other:
1. **Dependency Duplication & Security CVE Chaos**: Every microservice maintains its own `requirements.txt` with hardcoded versions of `Flask`, `requests`, `urllib3`, etc. Patching a zero-day vulnerability requires editing and redeploying 36 separate code repositories.
2. **Boilerplate Code Duplication**: Every microservice copy-pastes the same boilerplate code:
   - JSON structured logging configuration and regex PII data masking (masking credit cards, SSNs, authorization tokens).
   - Unified error handling and standard exception envelopes.
   - Kubernetes liveness and readiness actuator endpoints (`/health/liveness`, `/health/readiness`, `/info`, `/metrics`).
   - Latency timer interceptors and `X-Correlation-ID` header propagation.
   - Swagger UI and OpenAPI documentation hosting.

**The Solution**: Centralize **both** third-party library versions and common infrastructure components into a single internal enterprise Python package: **`enterprise-core-python`**.

---

## 2. Architectural Concept & Comparison to Spring Boot Starter

In the Java world, enterprises create a **Spring Boot Starter** (`corp-spring-boot-starter-web`) that brings in Spring Web, Jackson, Logback, and Actuator with pre-configured beans and pinned versions:

```
           JAVA SPRING BOOT STARTER                                 PYTHON ENTERPRISE CORE LIBRARY
┌──────────────────────────────────────────────┐          ┌──────────────────────────────────────────────┐
│       corp-spring-boot-starter-web           │          │            enterprise-core-python            │
├──────────────────────────────────────────────┤          ├──────────────────────────────────────────────┤
│ 1. Transitive Dependencies:                  │          │ 1. Transitive Dependencies:                  │
│    - spring-boot-starter-web: 3.2.0          │          │    - Flask==3.1.0, werkzeug==3.1.3           │
│    - logstash-logback-encoder: 7.4           │          │    - python-json-logger==2.0.7               │
│    - micrometer-core: 1.12.0                 │          │    - requests==2.32.3, urllib3==2.2.3        │
│    - jackson-databind: 2.16.0                │          │    - gunicorn==23.0.0, waitress==3.0.1       │
│                                              │          │    - pytest==8.3.3                           │
│ 2. Pre-Packaged Enterprise Beans:            │          │ 2. Pre-Packaged Enterprise Modules:          │
│    - GlobalControllerExceptionHandler        │          │    - setup_enterprise_logging() (PII Masking)│
│    - CorrelationIdFilter                     │          │    - register_enterprise_error_handlers()    │
│    - CustomActuatorEndpoint                  │          │    - register_latency_interceptors()         │
│    - SwaggerAutoConfiguration                │          │    - create_actuator_blueprint()             │
│                                              │          │    - register_swagger_ui()                   │
└──────────────────────┬───────────────────────┘          └──────────────────────┬───────────────────────┘
                       │                                                         │
          ┌────────────┴────────────┐                               ┌────────────┴────────────┐
          ▼                         ▼                               ▼                         ▼
┌──────────────────┐      ┌──────────────────┐            ┌──────────────────┐      ┌──────────────────┐
│ Microservice 1   │      │ Microservice 2   │            │ Microservice 1   │      │ Microservice 2   │
│ pom.xml:         │      │ pom.xml:         │            │ requirements.txt:│      │ requirements.txt:│
│ - corp-starter   │      │ - corp-starter   │            │ - enterprise-core│      │ - enterprise-core│
│ (NO OTHER DEPS)  │      │ (NO OTHER DEPS)  │            │ (NO OTHER DEPS)  │      │ (NO OTHER DEPS)  │
└──────────────────┘      └──────────────────┘            └──────────────────┘      └──────────────────┘
```

---

## 3. Anatomy of `enterprise-core-python`

The package is organized into modular, decoupled subsystems located under `enterprise-core-python/enterprise_core/`:

```text
enterprise-core-python/
├── setup.py                 # Package definition, metadata, and pinned dependencies
├── pyproject.toml           # Standard build backend configuration
├── tests/                   # Automated unit tests for all core modules
└── enterprise_core/
    ├── __init__.py          # Clean top-level public API exports
    ├── logging/             # JSON Structured Logging & PII Masking
    │   └── logger.py
    ├── exception/           # Unified Error Envelope & Exception Handlers
    │   └── handlers.py
    ├── interceptor/         # Latency & Correlation ID Interceptors
    │   └── interceptors.py
    ├── actuator/            # Health, Liveness, Readiness, Info, Metrics
    │   └── routes.py
    └── swagger/             # Swagger UI & OpenAPI Specification Engine
        └── swagger_ui.py
```

### 3.1 Structured Logging & PII Masking
The `setup_enterprise_logging(app, app_name)` function configures `python-json-logger` with an automated PII (Personally Identifiable Information) masking filter.
- Automatically redacts: Credit card numbers, Social Security Numbers (SSNs), email addresses, `Authorization: Bearer` tokens, and API keys.
- Ensures all logs are emitted as single-line JSON with timestamps, log levels, correlation IDs, and service names.

### 3.2 Enterprise Error Handling & Unified JSON Envelope
The `register_enterprise_error_handlers(app, default_prefix="CORE")` function registers global Flask error handlers that catch `EnterpriseBaseException`, HTTP exceptions (`400`, `404`, `405`, `500`), and uncaught exceptions.
Every error response strictly follows the enterprise JSON contract:
```json
{
  "timestamp": "2026-11-24T12:00:00.000000Z",
  "status": 404,
  "errorCode": "CESP_001",
  "errorMessage": "Exchange rate not available for requested pair",
  "errorDetailMessage": "Rate lookup for currency pair 'USD' -> 'XYZ' returned null in repository",
  "path": "/currency-exchange-service-python/currency-exchange/from/USD/to/XYZ",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "details": [
    "Ensure both fromCurrency and toCurrency exist in the rate dataset."
  ]
}
```

### 3.3 Latency & Correlation ID Interceptors
The `register_latency_interceptors(app, service_name)` hook instruments Flask's `@app.before_request` and `@app.after_request`:
- Extracts incoming `X-Correlation-ID` header (or generates a fresh UUIDv4).
- Injects `X-Correlation-ID` into the response header and logging context.
- Measures request processing time with microsecond accuracy and appends `X-Response-Time-Ms` to response headers.

### 3.4 Spring Boot-Style Actuator Health & Metrics Probes
The `create_actuator_blueprint(service_name, version, context_path)` generates a complete Flask Blueprint with production-ready endpoints:
- `GET <context_path>/health`: Aggregated health status.
- `GET <context_path>/health/liveness`: Kubernetes Liveness probe (returns `{"status": "UP", "probe": "liveness"}`).
- `GET <context_path>/health/readiness`: Kubernetes Readiness probe (returns `{"status": "UP", "probe": "readiness"}`).
- `GET <context_path>/info`: Service name, environment, and release version metadata.
- `GET <context_path>/metrics`: Runtime metrics (process uptime, memory consumption, request count).

### 3.5 Reusable OpenAPI 3.0 & Swagger UI Blueprint
The `register_swagger_ui(app, context_path, openapi_spec_dict, swagger_url="/swagger")` mounts an interactive Swagger UI rendered directly from an OpenAPI specification dictionary or YAML/JSON file without requiring third-party bulky extensions.

---

## 4. Step-by-Step Implementation Guide

### Step 4.1: Inspect the Library Structure & Dependencies (`setup.py`)

File: `enterprise-core-python/setup.py`
```python
from setuptools import setup, find_packages

setup(
    name="enterprise-core-python",
    version="1.0.0",
    description="Enterprise Core Library bundling dependencies, actuators, PII logging, and swagger",
    packages=find_packages(include=["enterprise_core", "enterprise_core.*"]),
    install_requires=[
        "Flask==3.1.0",
        "werkzeug==3.1.3",
        "python-json-logger==2.0.7",
        "requests==2.32.3",
        "urllib3==2.2.3",
        "gunicorn==23.0.0",
        "waitress==3.0.1",
        "pytest==8.3.3",
    ],
    extras_require={
        "aws": ["boto3==1.35.40"],
    },
    python_requires=">=3.10",
)
```

> [!IMPORTANT]
> All shared dependencies and their pinned security versions live **here in `setup.py`**. When a vulnerability is patched, it is modified here and nowhere else!

---

### Step 4.2: Build the Wheel Distribution

Build the binary `.whl` and source distribution `.tar.gz`:

```powershell
# Navigate to library folder
cd enterprise-core-python

# Install build tools if not present
pip install build wheel

# Build wheel package
python -m build

# Check output in dist/ folder
Get-ChildItem dist
# Produces: dist/enterprise_core_python-1.0.0-py3-none-any.whl
cd ..
```

---

### Step 4.3: Publishing to Internal Artifact Registries (Artifactory, Nexus, AWS, GCP)

Once built, the wheel is published to your enterprise package repository:

#### Option A: JFrog Artifactory / Sonatype Nexus
```powershell
pip install twine

# Publish to internal PyPI repository:
twine upload --repository-url https://artifactory.company.internal/artifactory/api/pypi/pypi-local dist/* `
    -u <USERNAME> -p <PASSWORD>
```

#### Option B: AWS CodeArtifact
```powershell
aws codeartifact login --tool twine --domain mycompany --repository internal-python-repo
twine upload --repository codeartifact dist/*
```

#### Option C: Google Cloud Artifact Registry
```powershell
pip install keyring keyrings.google-artifactregistry-auth
twine upload --repository-url https://us-central1-python.pkg.dev/my-project/internal-python-repo/ dist/*
```

---

### Step 4.4: Refactor Microservices to Consume `enterprise-core-python`

Because `enterprise-core-python` transitively brings in `Flask`, `requests`, `urllib3`, `gunicorn`, `waitress`, `python-json-logger`, and `pytest`, the microservices' `requirements.txt` are reduced to a single line:

#### 1. Currency Exchange Service
File: `currency-exchange-service-python/requirements.txt`
```text
enterprise-core-python
boto3
```

#### 2. Currency Conversion Service
File: `currency-conversion-service-python/requirements.txt`
```text
enterprise-core-python
```

> [!NOTE]
> Notice how clean this is! Zero hardcoded library versions. The microservice specifies only that it needs `enterprise-core-python` (and any cloud-specific SDK like `boto3`).

---

### Step 4.5: Bootstrap Enterprise Core in Microservice `app.py`

In each microservice, replace duplicate setup boilerplate with the clean enterprise helper functions:

File: `currency-exchange-service-python/app.py`
```python
from flask import Flask
from enterprise_core import (
    setup_enterprise_logging,
    register_enterprise_error_handlers,
    register_latency_interceptors,
    create_actuator_blueprint,
    register_swagger_ui
)

def create_app():
    app = Flask(__name__)
    context_path = "/currency-exchange-service-python"

    # 1. Initialize PII-Masking JSON Logger
    logger = setup_enterprise_logging(app, app_name="currency-exchange-service-python")

    # 2. Register Unified Error Envelope
    register_enterprise_error_handlers(app, default_prefix="CESP")

    # 3. Register Latency & Correlation ID Interceptor
    register_latency_interceptors(app, service_name="currency-exchange-service-python")

    # 4. Mount Actuators (/health, /liveness, /readiness, /info, /metrics)
    actuator_bp = create_actuator_blueprint(
        service_name="currency-exchange-service-python",
        version="1.0.0",
        context_path=context_path
    )
    app.register_blueprint(actuator_bp, url_prefix=context_path)

    # 5. Mount OpenAPI / Swagger UI
    from e2e.route.swagger_doc import OPENAPI_SPEC
    register_swagger_ui(app, context_path=context_path, openapi_spec_dict=OPENAPI_SPEC)

    # 6. Register Business Routes
    from e2e.route.exchange_routes import exchange_bp
    app.register_blueprint(exchange_bp, url_prefix=context_path)

    return app

app = create_app()
```

---

## 5. Local Development & Verification

### Editable Install Mode
During local development, install `enterprise-core-python` in editable mode (`-e`). Any code changes made to the core library are immediately reflected across both microservices without rebuilding:

```powershell
# 1. Install core library in editable mode
pip install -e ./enterprise-core-python

# 2. Install microservice dependencies
pip install -r currency-exchange-service-python/requirements.txt
pip install -r currency-conversion-service-python/requirements.txt
```

### Running Library and Microservice Tests
Verify that all unit tests across the library and both microservices pass:

```powershell
# Run enterprise-core library tests (PII masking, error handler, actuator probes)
pytest enterprise-core-python/tests -v

# Run Exchange Service tests
pytest currency-exchange-service-python/tests -v

# Run Conversion Service tests
pytest currency-conversion-service-python/tests -v
```

Expected result: **All test suites pass (100% Green)**.

---

## 6. Containerization & Docker Build Pipeline

### Consuming Wheels Locally in Docker
In our automated build script `build-and-push-docker.ps1`, before building the container images, the script automatically compiles the `enterprise-core-python` wheel and copies it into each service's build context:

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy local wheel package and install
COPY enterprise_core_python-*.whl ./
COPY requirements.txt ./
RUN pip install --no-cache-dir enterprise_core_python-*.whl && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . /app
USER 10001
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### Consuming Wheels from Private Artifactory / PyPI in Docker
In a production CI/CD pipeline, services don't need local wheel copies. They point directly to your internal JFrog Artifactory or Nexus server using `--extra-index-url`:

```dockerfile
RUN pip install --no-cache-dir \
    --extra-index-url https://__token__:${ARTIFACTORY_TOKEN}@artifactory.company.internal/artifactory/api/pypi/pypi-local/simple \
    -r requirements.txt
```

### Docker Compose Smoke Testing

Build and run the entire ecosystem:
```powershell
# Build container images
.\build-and-push-docker.ps1 -Tag latest

# Spin up containers
docker compose up -d
```

Verify the live endpoints:
```powershell
# 1. Exchange Service Actuator Liveness Probe (Provided by enterprise-core!)
curl http://localhost:8000/currency-exchange-service-python/health/liveness

# 2. Exchange Service Actuator Metrics
curl http://localhost:8000/currency-exchange-service-python/metrics

# 3. Exchange Rate API
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR

# 4. Conversion Service API (Calculates 10 USD -> INR)
curl http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10
```

Stop containers:
```powershell
docker compose down
```

---

## 7. How to Patch a Security Vulnerability (CVE) in Seconds

Suppose a critical CVE is reported in `requests` or `urllib3`:

1. **Bump Version in One Single File**:
   Open `enterprise-core-python/setup.py`:
   ```python
   install_requires=[
       "requests==2.32.4",  # Patched!
       "urllib3==2.2.4",     # Patched!
       ...
   ]
   ```
   Bump library version from `1.0.0` to `1.0.1`.

2. **Publish New Wheel**:
   ```powershell
   python -m build
   twine upload --repository-url https://artifactory.internal/... dist/*
   ```

3. **Redeploy All 36+ Microservices**:
   Because the microservices declare:
   ```text
   enterprise-core-python>=1.0.0
   ```
   During the next container build, pip automatically downloads the new `1.0.1` wheel.
   **Zero microservice repositories are touched.** Both the core library update and the vulnerability patch propagate across the entire fleet simultaneously!

---

## 8. CLI Command Reference & Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Build Enterprise Core Wheel** | `cd enterprise-core-python; python -m build; cd ..` |
| **Install in Editable Mode** | `pip install -e ./enterprise-core-python` |
| **Run Enterprise Core Tests** | `pytest enterprise-core-python/tests -v` |
| **Run Microservice Tests** | `pytest currency-exchange-service-python/tests -v` |
| **Publish Wheel to Artifactory** | `twine upload --repository-url <URL> enterprise-core-python/dist/*` |
| **Build Container Images** | `.\build-and-push-docker.ps1 -Tag latest` |
| **Start Containers** | `docker compose up -d` |
| **Test Live Health Actuator** | `curl http://localhost:8000/currency-exchange-service-python/health/liveness` |
| **Test Live Swagger UI** | Open browser to `http://localhost:8000/currency-exchange-service-python/swagger` |
| **Stop Containers** | `docker compose down` |
