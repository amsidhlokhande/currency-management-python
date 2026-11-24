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
6. [Containerization & Dual Docker Compose Architecture](#6-containerization--dual-docker-compose-architecture)
   - [6.1 Git-Based Dependency Distribution in Docker](#61-git-based-dependency-distribution-in-docker)
   - [6.2 Architecture of Dual Docker Compose Workflows](#62-architecture-of-dual-docker-compose-workflows)
   - [6.3 Local Build & Push Setup (`docker-compose.build.yml`)](#63-local-build--push-setup-docker-composebuildyml)
   - [6.4 Zero-Build Remote Setup (`docker-compose.pull.yml`)](#64-zero-build-remote-setup-docker-composepullyml)
   - [6.5 Automation via `build-and-push-docker.ps1`](#65-automation-via-build-and-push-dockerps1)
   - [6.6 Environment Variables & Direct Docker Compose CLI Commands](#66-environment-variables--direct-docker-compose-cli-commands)
   - [6.7 End-to-End Verification & Smoke Testing](#67-end-to-end-verification--smoke-testing)
7. [How to Patch a Security Vulnerability (CVE) in Seconds](#7-how-to-patch-a-security-vulnerability-cve-in-seconds)
8. [The Ultimate Balance: Zero Code Maintenance vs. Enterprise-Grade Release Control](#8-the-ultimate-balance-zero-code-maintenance-vs-enterprise-grade-release-control)
   - [8.1 The Enterprise Dilemma in 36+ Microservices](#81-the-enterprise-dilemma-in-36-microservices)
   - [8.2 Decoupled Architecture Mechanics (Docker ARG Injection)](#82-decoupled-architecture-mechanics-docker-arg-injection)
   - [8.3 Enterprise Release Milestones & Production Freezes](#83-enterprise-release-milestones--production-freezes)
   - [8.4 Instant Zero-PR Production Rollbacks](#84-instant-zero-pr-production-rollbacks)
   - [8.5 Canary & Selective Upgrades](#85-canary--selective-upgrades)
   - [8.6 CI/CD Pipeline Automation in GitHub Actions](#86-cicd-pipeline-automation-in-github-actions)
9. [CLI Command Reference & Cheat Sheet](#9-cli-command-reference--cheat-sheet)

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

Because `enterprise-core-python` transitively brings in `Flask`, `requests`, `urllib3`, `gunicorn`, `waitress`, `python-json-logger`, and `pytest`, the microservices' `requirements.txt` specify only `enterprise-core-python` (plus any cloud-specific SDK like `boto3`):

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
> Notice how clean this is! Zero hardcoded third-party library versions and **zero hardcoded Git URLs or tags**. The microservice specifies only that it depends on `enterprise-core-python`, completely eliminating maintenance overhead across downstream services. All transitive dependencies are managed centrally by the core library, and the exact repository or tag version is resolved flexibly during containerization and CI/CD via build arguments.

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

## 6. Containerization & Dual Docker Compose Architecture

### 6.1 Git-Based Dependency Distribution in Docker

In modern enterprise architectures, microservice container builds **do not copy loose local `.whl` files** across folders. Furthermore, microservices **do not hardcode Git tags or URLs inside their `requirements.txt`**. Instead, each microservice consumes `enterprise-core-python` as a decoupled dependency resolved dynamically through Docker build arguments:

```text
# requirements.txt
enterprise-core-python
```

To support this in automated container builds while adhering to zero-trust principles:
1. **Dynamic Build-Time Resolution (`ARG ENTERPRISE_CORE_REPO`)**: By default, the builder pulls from the `main` branch of the centralized repository. If an immutable tag or branch is required for production, it is passed externally via `--build-arg ENTERPRISE_CORE_REPO=...` without modifying source code.
2. **Pre-Installation into Virtual Environment**: The Dockerfile installs `git+${ENTERPRISE_CORE_REPO}` directly into `/opt/venv` before running `pip install -r requirements.txt`. This satisfies `enterprise-core-python` ahead of time and automatically installs all transitive dependencies.
3. **Multi-Stage Build Isolation**: The build environment uses `ARG GITHUB_TOKEN` (via `x-access-token`) in the builder stage to authenticate Git operations if required, with an automated fallback to anonymous public clone if the token is omitted or unauthorized. Build tokens are completely discarded before copying the final virtual environment (`/opt/venv`) into the hardened runtime image.
4. **Non-Root Hardened Runtime**: The runtime image runs as an unprivileged non-root user (`appuser`, UID `10001`), protecting the host from container breakouts.
5. **Context Path Health Probes**: Container healthchecks query the native `/health/liveness` probe mounted under each service's dedicated context path.

```dockerfile
# Stage 1: Build & Dependencies Layer
FROM python:3.12-slim AS builder
WORKDIR /build

ARG GITHUB_TOKEN
ARG ENTERPRISE_CORE_REPO=https://github.com/amsidhlokhande/enterprise-core-python.git

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential curl && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN if [ -n "$GITHUB_TOKEN" ]; then \
        git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi && \
    pip install --upgrade pip && \
    (pip install --no-cache-dir "git+${ENTERPRISE_CORE_REPO}" || ( \
        echo "Authenticated clone failed or repository is public, retrying without token..." && \
        rm -f ~/.gitconfig /root/.gitconfig && \
        pip install --no-cache-dir "git+${ENTERPRISE_CORE_REPO}" \
    )) && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Hardened Production Runtime
FROM python:3.12-slim AS runner
WORKDIR /app

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup . /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER 10001
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "app:app"]
```

---

### 6.2 Architecture of Dual Docker Compose Workflows

To satisfy both developer agility (local iteration) and production-grade parity (zero-build verification), the repository provides two distinct Docker Compose configurations:

```mermaid
flowchart TD
    subgraph LocalDev ["Workflow A: Local Build & Push (docker-compose.build.yml)"]
        LocalSrc["📁 Local Source Code<br/>• Dockerfile (Multi-stage)<br/>• requirements.txt (@v1.0.0)"]
        BuildEngine["🔨 Docker Build Engine<br/>• Build-arg: GITHUB_TOKEN / READ_PACKAGES_TOKEN<br/>• git clone enterprise-core-python@v1.0.0"]
        LocalTag["🏷️ Tag Images<br/>${DOCKER_USERNAME}/currency-exchange-service-python:latest<br/>${DOCKER_USERNAME}/currency-conversion-service-python:latest"]
        DockerHubRegistry[("🐳 Docker Hub Registry<br/>hub.docker.com/u/${DOCKER_USERNAME}")]
        LocalSrc --> BuildEngine --> LocalTag -->|docker compose push| DockerHubRegistry
    end

    subgraph ZeroBuild ["Workflow B: Zero-Build Pull & Run (docker-compose.pull.yml)"]
        DockerHubPrebuilt[("🐳 Docker Hub Registry<br/>Pre-built images")]
        DockerPull["📥 Docker Engine Pull<br/>• Zero local compilation<br/>• Zero build arguments"]
        DockerHubPrebuilt --> DockerPull
    end

    subgraph Runtime ["Docker Desktop Runtime Mesh"]
        DesktopMesh["🌐 Network: currency-mesh<br/>• currency-exchange-service-python (Port: 8000)<br/>• currency-conversion-service-python (Port: 8100)"]
    end

    LocalTag -->|docker compose up| DesktopMesh
    DockerPull -->|docker compose up| DesktopMesh
```

---

### 6.3 Local Build & Push Setup (`docker-compose.build.yml`)

The file `docker-compose.build.yml` compiles images locally from source using each microservice's multi-stage `Dockerfile`, securely forwarding `READ_PACKAGES_TOKEN` (or `GITHUB_TOKEN`) for private repository access, tagging the images with `${DOCKER_USERNAME}`, pushing them to Docker Hub, and running them on Docker Desktop:

```yaml
version: "3.8"

networks:
  currency-mesh:
    driver: bridge

services:
  currency-exchange-service-python:
    build:
      context: ./currency-exchange-service-python
      dockerfile: Dockerfile
      args:
        GITHUB_TOKEN: ${READ_PACKAGES_TOKEN:-${GITHUB_TOKEN:-}}
    image: ${DOCKER_USERNAME:-amsidhlokhande}/currency-exchange-service-python:latest
    container_name: currency-exchange-service-python
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - ENV=docker
      - LOG_LEVEL=INFO
      - CONTEXT_PATH=/currency-exchange-service-python
      - RATES_CSV_PATH=data/exchange_rates.csv
    networks:
      - currency-mesh
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/currency-exchange-service-python/health/liveness')"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped

  currency-conversion-service-python:
    build:
      context: ./currency-conversion-service-python
      dockerfile: Dockerfile
      args:
        GITHUB_TOKEN: ${READ_PACKAGES_TOKEN:-${GITHUB_TOKEN:-}}
    image: ${DOCKER_USERNAME:-amsidhlokhande}/currency-conversion-service-python:latest
    container_name: currency-conversion-service-python
    ports:
      - "8100:8100"
    environment:
      - PORT=8100
      - ENV=docker
      - LOG_LEVEL=INFO
      - CONTEXT_PATH=/currency-conversion-service-python
      - EXCHANGE_SERVICE_URL=http://currency-exchange-service-python:8000/currency-exchange-service-python
    depends_on:
      currency-exchange-service-python:
        condition: service_healthy
    networks:
      - currency-mesh
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8100/currency-conversion-service-python/health/liveness')"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
```

> [!TIP]
> Use `docker-compose.build.yml` when making active source code modifications, updating endpoints, or testing new dependency versions before publishing to Docker Hub.

---

### 6.4 Zero-Build Remote Setup (`docker-compose.pull.yml`)

The file `docker-compose.pull.yml` provides a **zero-build** experience. It contains no `build:` directives and exclusively pulls certified images from Docker Hub (`${DOCKER_USERNAME}/<service>:latest`) using credentials supplied via `DOCKER_USERNAME` and `DOCKER_PASSWORD`:

```yaml
version: "3.8"

networks:
  currency-mesh:
    driver: bridge

services:
  currency-exchange-service-python:
    image: ${DOCKER_USERNAME:-amsidhlokhande}/currency-exchange-service-python:latest
    container_name: currency-exchange-service-python
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - ENV=docker
      - LOG_LEVEL=INFO
      - CONTEXT_PATH=/currency-exchange-service-python
      - RATES_CSV_PATH=data/exchange_rates.csv
    networks:
      - currency-mesh
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/currency-exchange-service-python/health/liveness')"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped

  currency-conversion-service-python:
    image: ${DOCKER_USERNAME:-amsidhlokhande}/currency-conversion-service-python:latest
    container_name: currency-conversion-service-python
    ports:
      - "8100:8100"
    environment:
      - PORT=8100
      - ENV=docker
      - LOG_LEVEL=INFO
      - CONTEXT_PATH=/currency-conversion-service-python
      - EXCHANGE_SERVICE_URL=http://currency-exchange-service-python:8000/currency-exchange-service-python
    depends_on:
      currency-exchange-service-python:
        condition: service_healthy
    networks:
      - currency-mesh
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8100/currency-conversion-service-python/health/liveness')"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
```

> [!IMPORTANT]
> `docker-compose.pull.yml` is ideal for QA teams, DevOps engineers, and CI/CD pipelines that need to spin up the entire microservices mesh instantly without requiring a Python compiler, git build tools, or access tokens.

---

### 6.5 Automation via `build-and-push-docker.ps1`

The root orchestrator script [`build-and-push-docker.ps1`](file:///C:/Users/amsid/projects/python_projects/currency-management-python/build-and-push-docker.ps1) automates all build, push, pull, and execution steps across both Compose configurations.

#### Parameter Reference:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-Action` | String | `BuildPushRun` | Execution mode: `BuildPushRun`, `PullAndRun`, `BuildOnly`, `BuildAndPush`, `Down`. |
| `-Registry` | String | `$env:DOCKER_USERNAME` or `amsidhlokhande` | Target Docker Hub namespace / registry. |
| `-Tag` | String | `latest` | Tag applied to container images. |

#### Supported Actions:
1. **`BuildPushRun`** (Default):
   - Authenticates to Docker Hub if `DOCKER_USERNAME` and `DOCKER_PASSWORD` are present.
   - Builds container images locally using `docker-compose.build.yml` with Git auth tokens.
   - Pushes tagged images (`${DOCKER_USERNAME}/<service>:latest`) to Docker Hub.
   - Launches both services on Docker Desktop in detached mode (`-d`).
   ```powershell
   .\build-and-push-docker.ps1 -Action BuildPushRun
   ```

2. **`PullAndRun`** (Zero-Build Mode):
   - Authenticates to Docker Hub.
   - Pulls pre-built images directly from Docker Hub via `docker-compose.pull.yml`.
   - Launches both services on Docker Desktop without compiling anything locally.
   ```powershell
   .\build-and-push-docker.ps1 -Action PullAndRun
   ```

3. **`BuildOnly`**:
   - Compiles container images locally via `docker-compose.build.yml` without pushing to Docker Hub or starting containers.
   ```powershell
   .\build-and-push-docker.ps1 -Action BuildOnly
   ```

4. **`BuildAndPush`**:
   - Builds images locally and pushes them to Docker Hub without starting local containers (ideal for automated CI runners).
   ```powershell
   .\build-and-push-docker.ps1 -Action BuildAndPush
   ```

5. **`Down`**:
   - Stops and removes all running containers, networks, and volumes for both Compose setups.
   ```powershell
   .\build-and-push-docker.ps1 -Action Down
   ```

---

### 6.6 Environment Variables & Direct Docker Compose CLI Commands

#### Required & Optional Environment Variables:
| Variable Name | Required For | Description |
| :--- | :--- | :--- |
| `DOCKER_USERNAME` | Pushing / Pulling from Docker Hub | Your Docker Hub account username (e.g. `amsidhlokhande`). Defaults to `amsidhlokhande`. |
| `DOCKER_PASSWORD` | Automated Docker Login | Your Docker Hub Personal Access Token (PAT) or account password. |
| `READ_PACKAGES_TOKEN` | Local Image Building | GitHub Personal Access Token (PAT) with `read:packages` / `repo` permissions to clone `enterprise-core-python`. |
| `GITHUB_TOKEN` | Local Image Building | Fallback token used interchangeably with `READ_PACKAGES_TOKEN`. |

#### Direct Docker Compose CLI Commands:
For power users who prefer running `docker compose` directly without the PowerShell wrapper:

```powershell
# Set environment variables in your PowerShell session
$env:DOCKER_USERNAME = "amsidhlokhande"
$env:READ_PACKAGES_TOKEN = "ghp_yourPersonalAccessTokenHere"

# -------------------------------------------------------------
# Option 1: Local Build & Run Workflow (docker-compose.build.yml)
# -------------------------------------------------------------
# Build images from local Dockerfiles:
docker compose -f docker-compose.build.yml build

# Push built images to Docker Hub:
docker compose -f docker-compose.build.yml push

# Launch containers on Docker Desktop:
docker compose -f docker-compose.build.yml up -d

# -------------------------------------------------------------
# Option 2: Zero-Build Remote Pull Workflow (docker-compose.pull.yml)
# -------------------------------------------------------------
# Pull pre-built images from Docker Hub:
docker compose -f docker-compose.pull.yml pull

# Launch containers without local build:
docker compose -f docker-compose.pull.yml up -d

# -------------------------------------------------------------
# Teardown
# -------------------------------------------------------------
docker compose -f docker-compose.build.yml down
# or
docker compose -f docker-compose.pull.yml down
```

---

### 6.7 End-to-End Verification & Smoke Testing

Once containers are launched (via either `docker-compose.build.yml` or `docker-compose.pull.yml`), verify the live endpoints under each service's context path:

```powershell
# 1. Exchange Service Actuator Liveness Probe (Provided by enterprise-core!)
curl -i http://localhost:8000/currency-exchange-service-python/health/liveness

# 2. Exchange Service Actuator Metrics
curl -i http://localhost:8000/currency-exchange-service-python/metrics

# 3. Exchange Rate Lookup API
curl -i http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR

# 4. Conversion Service API (Converts 10 USD to INR via inter-service mesh call)
curl -i http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10 `
    -H "X-Correlation-ID: smoke-test-101"
```

Expected Conversion Response:
```json
{
  "id": 1001,
  "fromCurrency": "USD",
  "toCurrency": "INR",
  "conversionMultiple": 86.50,
  "quantity": 10.0,
  "totalCalculatedAmount": 865.00,
  "environment": "currency-conversion-service-python:8100",
  "exchangeServiceEnvironment": "currency-exchange-service-python:8000",
  "correlationId": "smoke-test-101"
}
```

---

## 7. How to Patch a Security Vulnerability (CVE) in Seconds

Suppose a critical CVE is reported in `requests` or `urllib3`:

1. **Bump Version in One Single Repository**:
   Open `enterprise-core-python/setup.py` and `enterprise-core-python/pyproject.toml`:
   ```python
   install_requires=[
       "requests==2.32.4",  # Patched!
       "urllib3==2.2.4",     # Patched!
       ...
   ]
   ```
   Commit and push to `main` (or tag a patch release `v1.0.1`).

2. **Publish Automated Git Release (Optional)**:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
   The GitHub Actions workflow [`.github/workflows/enterprise-core-release.yml`](.github/workflows/enterprise-core-release.yml) automatically runs tests, builds distribution wheels, and creates the release.

3. **Propagate to All 36 Microservices with Zero Code PRs**:
   Downstream microservice `requirements.txt` files **do not need to be touched**! They continue to state simply:
   ```text
   enterprise-core-python
   ```
   Triggering your CI/CD pipelines or running:
   ```powershell
   .\build-and-push-docker.ps1 -Action BuildPushRun
   ```
   The multi-stage builder pulls the updated centralized code, transitively updates `requests` and `urllib3`, and builds hardened, patched images deployed across Docker Desktop or Kubernetes immediately.

---

## 8. The Ultimate Balance: Zero Code Maintenance vs. Enterprise-Grade Release Control

### 8.1 The Enterprise Dilemma in 36+ Microservices

In enterprise systems comprising dozens of microservices, software architects traditionally confront an agonizing tradeoff between developer agility and operational stability:

```
                      ┌──────────────────────────────────────────────┐
                      │     The Microservices Dependency Dilemma     │
                      └──────────────────────┬───────────────────────┘
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             ▼                                                               ▼
┌──────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│   Approach A: Hardcoded in Code          │   │   Approach B: Always Main Branch         │
│   (requirements.txt @ v1.2.0)            │   │   (git+https://.../repo.git)             │
├──────────────────────────────────────────┤   ├──────────────────────────────────────────┤
│ ❌ 36 PRs needed for every bug fix       │   │ ❌ Accidental breaking change on `main`  │
│ ❌ Engineers spend days bumping versions │   │    instantly breaks all 36 services      │
│ ❌ Merge fatigue & high review overhead  │   │ ❌ Cannot guarantee reproducible builds │
│ ✅ Strict version control in production  │   │ ✅ Zero code maintenance                 │
└──────────────────────────────────────────┘   └──────────────────────────────────────────┘
```

If you pin versions inside source code files (`requirements.txt`), any minor bug fix or CVE remediation requires creating, reviewing, testing, and merging **36 separate Pull Requests**. This results in PR fatigue, merge bottlenecks, and services lagging behind on critical security updates.

Conversely, if services always pull from `main` without version safeguards, an unintentional breaking commit pushed to the centralized library could break downstream CI builds or compromise production environments simultaneously.

### 8.2 Decoupled Architecture Mechanics (Docker ARG Injection)

The architecture implemented in this repository achieves the **ultimate balance**:
- **Application Code is Decoupled**: Each microservice declares only `enterprise-core-python` in its `requirements.txt`. No Git URLs, no commit hashes, no version numbers.
- **Release Control is Externalized**: The version resolution is handled at container build time via Docker `ARG` and CI/CD parameters.

```mermaid
flowchart TD
    subgraph Central ["1. Central Core Repository (enterprise-core-python)"]
        CommitMain["commit on main<br/>(Continuous Dev / Fixes)"]
        GitTag["Git Tag: v1.2.0<br/>(Audited Release Milestone)"]
    end

    subgraph Trigger ["2. Deployment & Build Trigger"]
        DevEnv["Dev / Feature CI Build<br/>(Default: No Arg -> main)"]
        ProdEnv["Production Release Build<br/>(Pass --build-arg @v1.2.0)"]
    end

    subgraph Downstream ["3. Downstream Microservices (36 Services)"]
        MS1["currency-exchange-service<br/>requirements.txt = enterprise-core-python"]
        MS2["currency-conversion-service<br/>requirements.txt = enterprise-core-python"]
        MS36["service-36<br/>requirements.txt = enterprise-core-python"]
    end

    CommitMain --> DevEnv
    GitTag --> ProdEnv

    DevEnv -->|Pulls latest main (Zero Touch)| Downstream
    ProdEnv -->|Pulls frozen v1.2.0 (Audit Parity)| Downstream
```

In the Dockerfile:
```dockerfile
# Default fallback: Tracks latest 'main' branch automatically
ARG ENTERPRISE_CORE_REPO=https://github.com/amsidhlokhande/enterprise-core-python.git

RUN pip install --no-cache-dir "git+${ENTERPRISE_CORE_REPO}" && \
    pip install --no-cache-dir -r requirements.txt
```

When building:
1. **Default (Zero Overhead)**: If no build argument is supplied, Docker pulls from `main`. Developers and CI pipelines always build against the latest vetted core library without touching code.
2. **Controlled (Audit Freezes)**: If an exact tag or commit is required, Docker overrides the variable via `--build-arg ENTERPRISE_CORE_REPO=...` without altering a single source file.

### 8.3 Enterprise Release Milestones & Production Freezes

When preparing for an enterprise production release, change freeze, or compliance audit (e.g., SOC2, PCI-DSS):
1. Create an immutable Git tag in `enterprise-core-python`:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```
2. Build production container images by supplying the tag in the build command:
   ```powershell
   docker build \
     --build-arg ENTERPRISE_CORE_REPO=https://github.com/amsidhlokhande/enterprise-core-python.git@v1.2.0 \
     -t ${DOCKER_USERNAME}/currency-exchange-service-python:v1.2.0 .
   ```
3. Even if experimental commits are subsequently merged to `enterprise-core-python`'s `main` branch, all production container builds remain **100% frozen, immutable, and reproducible**.

### 8.4 Instant Zero-PR Production Rollbacks

Consider a catastrophic production incident: an upgrade introduced an unforeseen regression in the shared database connection pool or error interceptor.

- **Traditional Approach (Hardcoded `requirements.txt`)**:
  - Open 36 PRs across 36 repositories reverting the tag from `v1.3.0` back to `v1.2.0`.
  - Wait for 36 continuous integration pipelines to run unit tests.
  - Wait for approvals and merge all 36 PRs.
  - Time to resolution: **Hours to days**.
- **Decoupled Build-Arg Pattern**:
  - Update **one single configuration variable** in your deployment pipeline or Helm chart (`CORE_VERSION: v1.2.0`).
  - Re-run the release pipeline. All 36 services immediately build and deploy using the verified `v1.2.0` library.
  - Time to resolution: **Minutes. Zero code changes. Zero PRs.**

### 8.5 Canary & Selective Upgrades

When testing major library refactors (e.g., migrating to `enterprise-core-python@v2.0.0-rc1`):
- You can test the upgrade against **one canary microservice** (`currency-conversion-service`) by setting `--build-arg ENTERPRISE_CORE_REPO=...@v2.0.0-rc1` for that service's build job.
- The remaining 35 microservices continue running safely on `v1.2.0`.
- Neither the canary service nor the production services require custom branches or temporary git commits.

### 8.6 CI/CD Pipeline Automation in GitHub Actions

This balance is implemented cleanly in GitHub Actions via parameterized workflows ([`.github/workflows/docker-build-push.yml`](.github/workflows/docker-build-push.yml)):

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:
    inputs:
      core_library_version:
        description: 'Enterprise Core Tag/Branch (e.g., v1.2.0 or leave blank for main)'
        required: false
        default: ''

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Microservice Source Code
        uses: actions/checkout@v4

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/currency-exchange-service-python:latest
          build-args: |
            GITHUB_TOKEN=${{ secrets.READ_PACKAGES_TOKEN }}
            ENTERPRISE_CORE_REPO=https://github.com/amsidhlokhande/enterprise-core-python.git${{ inputs.core_library_version != '' && format('@{0}', inputs.core_library_version) || '' }}
```

---

## 9. CLI Command Reference & Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Run Enterprise Core Unit Tests** | `pytest enterprise-core-python/tests -v` |
| **Run Exchange Service Unit Tests** | `pytest currency-exchange-service-python/tests -v` |
| **Run Conversion Service Unit Tests**| `pytest currency-conversion-service-python/tests -v` |
| **Local Editable Install** | `pip install -e ./enterprise-core-python` |
| **Build & Push & Run (All-in-One)** | `.\build-and-push-docker.ps1 -Action BuildPushRun` |
| **Zero-Build Pull & Run from Docker Hub** | `.\build-and-push-docker.ps1 -Action PullAndRun` |
| **Build Local Images Only** | `.\build-and-push-docker.ps1 -Action BuildOnly` |
| **Build and Push to Registry Only** | `.\build-and-push-docker.ps1 -Action BuildAndPush` |
| **Tear Down Docker Compose Mesh** | `.\build-and-push-docker.ps1 -Action Down` |
| **Direct Compose: Build & Start** | `docker compose -f docker-compose.build.yml up -d --build` |
| **Direct Compose: Zero-Build Start** | `docker compose -f docker-compose.pull.yml pull && docker compose -f docker-compose.pull.yml up -d` |
| **Test Live Health Actuator** | `curl http://localhost:8000/currency-exchange-service-python/health/liveness` |
| **Test Live Swagger UI** | Open browser to `http://localhost:8000/currency-exchange-service-python/swagger` |

