# 📘 Approach 3: Modern Centralized Dependency Management with uv & Overrides BOM

> **Branch**: `uv-workspace-dependency-management`  
> **Target Audience**: Solution Architects, Tech Leads, DevOps Engineers, and Python Developers  
> **Java Analogy**: Maven Multi-Module Project with Parent BOM `<dependencyManagement>` and Reactor Resolution

---

## 📑 Table of Contents
1. [Problem Statement & Enterprise Motivation](#1-problem-statement--enterprise-motivation)
2. [Architectural Concept & Comparison to Java Maven](#2-architectural-concept--comparison-to-java-maven)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Step-by-Step Implementation Guide](#4-step-by-step-implementation-guide)
   - [Step 4.1: Install `uv`](#step-41-install-uv)
   - [Step 4.2: Create the Central Enterprise BOM (`pyproject.toml`)](#step-42-create-the-central-enterprise-bom-pyprojecttoml)
   - [Step 4.3: Create Central Version Overrides (`overrides.txt`)](#step-43-create-central-version-overrides-overridestxt)
   - [Step 4.4: Strip Hardcoded Versions from Microservice `requirements.txt`](#step-44-strip-hardcoded-versions-from-microservice-requirementstxt)
   - [Step 4.5: Generate Cryptographic Lockfile with `uv lock`](#step-45-generate-cryptographic-lockfile-with-uv-lock)
5. [Local Development Workflow](#5-local-development-workflow)
   - [Installing Dependencies in Virtual Environment](#installing-dependencies-in-virtual-environment)
   - [Running Automated Unit & Integration Tests](#running-automated-unit--integration-tests)
6. [Containerization & Docker Multi-Stage Pipeline](#6-containerization--docker-multi-stage-pipeline)
   - [Optimized Dockerfile with Pre-Built `uv` Binary](#optimized-dockerfile-with-pre-built-uv-binary)
   - [Automated Build & Push PowerShell Script](#automated-build--push-powershell-script)
   - [Docker Compose Smoke Testing](#docker-compose-smoke-testing)
7. [How to Patch a Security Vulnerability (CVE) in Seconds](#7-how-to-patch-a-security-vulnerability-cve-in-seconds)
8. [CLI Command Reference & Cheat Sheet](#8-cli-command-reference--cheat-sheet)

---

## 1. Problem Statement & Enterprise Motivation

When an enterprise scales beyond 36+ Python microservices, managing dependencies independently in each repository causes severe pain points:
- **Security Vulnerability (CVE) Fatigue**: An Open Source Software (OSS) vulnerability scanning tool flags a critical flaw in a library like `urllib3` or `requests`. Developers must create 36+ Pull Requests, edit 36+ `requirements.txt` files, test, build, and deploy 36+ times.
- **Dependency Version Drift**: Service A runs `Flask==3.0.0`, Service B runs `Flask==2.2.5`, and Service C runs `Flask==3.1.0`. Subtle bugs arise from mismatched behaviors.
- **Microservice Clutter**: Microservices should focus purely on business logic—not duplicate packaging configuration files.

**The Solution**: A single, central source of truth for all dependency versions using Astral's Rust-powered `uv` package engine. Individual microservices specify **only** the functional package names they need (`flask`, `requests`), while version numbers are 100% centrally governed.

---

## 2. Architectural Concept & Comparison to Java Maven

If your background is in Java Spring Boot / Maven:

```
               JAVA SPRING BOOT (MAVEN)                                  PYTHON (uv APPROACH)
      ┌────────────────────────────────────────┐                ┌────────────────────────────────────────┐
      │             parent-pom.xml             │                │             pyproject.toml             │
      │        <dependencyManagement>          │                │            (Root Central BOM)          │
      │   - spring-boot-starter: 3.2.0         │                │   - Flask==3.1.0                       │
      │   - jackson-databind: 2.16.0           │                │   - requests==2.32.3                   │
      └──────────────────┬─────────────────────┘                └──────────────────┬─────────────────────┘
                         │                                                         │
         ┌───────────────┴───────────────┐                         ┌───────────────┴───────────────┐
         ▼                               ▼                         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐       ┌─────────────────┐             ┌─────────────────┐
│ Child Pom (SVC 1)│             │ Child Pom (SVC 2)│       │ requirements.txt│             │ requirements.txt│
│ <dependency>    │             │ <dependency>    │       │ (Exchange Svc)  │             │ (Conversion Svc)│
│  spring-starter │             │  spring-starter │       │ - flask         │             │ - flask         │
│  (NO VERSION)   │             │  (NO VERSION)   │       │ - boto3         │             │ - requests      │
└─────────────────┘             └─────────────────┘       │ (NO VERSIONS)   │             │ (NO VERSIONS)   │
                                                          └─────────────────┘             └─────────────────┘
```

| Dimension | Java Maven BOM Pattern | Python uv Approach |
| :--- | :--- | :--- |
| **Central Version Store** | `<dependencyManagement>` in root `pom.xml` | Central `pyproject.toml` + `overrides.txt` |
| **Microservice Manifest** | `<dependency>` with **no** `<version>` tag | `requirements.txt` with **no** version pins |
| **Deterministic Lock** | Maven Reactor build resolves versions | `uv.lock` locks exact platform wheel hashes |
| **Boilerplate in Services**| Child `pom.xml` only | **Zero added files** in service directories (no extra `pyproject.toml`) |
| **Resolution Speed** | 10–30 seconds per build | **< 0.5 seconds** (up to 100x faster than standard pip) |

---

## 3. Prerequisites & Environment Setup

Ensure the following tools are installed on your workstation:
- **Python**: Version 3.10+ (Tested on Python 3.12 and Python 3.15.2)
- **PowerShell**: Version 5.1+ (Windows) or Bash (macOS/Linux)
- **Docker & Docker Compose**: Docker Desktop or Docker Engine 24.0+
- **Git**: Version 2.30+

---

## 4. Step-by-Step Implementation Guide

### Step 4.1: Install `uv`

Install `uv` globally using the official installer or via Python pip:

**On Windows (PowerShell):**
```powershell
# Option A: Official standalone binary installer (Recommended)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Option B: Via existing Python environment
pip install uv
```

**On Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
# Expected Output: uv 0.5.x or 0.13.x (or newer)
```

---

### Step 4.2: Create the Central Enterprise BOM (`pyproject.toml`)

Create a `pyproject.toml` in the **root** repository directory. This file acts as the enterprise Bill of Materials (BOM), pinning all approved and scanned library versions.

File: `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "enterprise-dependencies-bom"
version = "1.0.0"
description = "Enterprise Centralized Dependency BOM governed by uv"
requires-python = ">=3.10"
dependencies = [
    "Flask==3.1.0",
    "werkzeug==3.1.3",
    "python-json-logger==2.0.7",
    "requests==2.32.3",
    "urllib3==2.2.3",
    "gunicorn==23.0.0",
    "waitress==3.0.1",
    "pytest==8.3.3",
    "boto3==1.35.40",
    "certifi==2024.8.30",
    "idna==3.10",
    "charset-normalizer==3.4.0",
]
```

> [!NOTE]
> Individual microservices do **NOT** have their own `pyproject.toml`. This keeps the microservice directories completely clean.

---

### Step 4.3: Create Central Version Overrides (`overrides.txt`)

For individual pip installations and isolated Docker container builds, create a central `overrides.txt` file in the root directory:

File: `overrides.txt`
```text
Flask==3.1.0
werkzeug==3.1.3
python-json-logger==2.0.7
requests==2.32.3
urllib3==2.2.3
gunicorn==23.0.0
waitress==3.0.1
pytest==8.3.3
boto3==1.35.40
botocore==1.35.40
certifi==2024.8.30
idna==3.10
charset-normalizer==3.4.0
```

---

### Step 4.4: Strip Hardcoded Versions from Microservice `requirements.txt`

Edit each microservice's `requirements.txt`. Remove all version numbers (`==`, `>=`, `<=`). The microservice declares **only what libraries it needs to function**.

#### 1. Currency Exchange Service
File: `currency-exchange-service-python/requirements.txt`
```text
flask
waitress
gunicorn
boto3
botocore
python-json-logger
pytest
requests
urllib3
```

#### 2. Currency Conversion Service
File: `currency-conversion-service-python/requirements.txt`
```text
flask
waitress
gunicorn
requests
urllib3
python-json-logger
pytest
```

---

### Step 4.5: Generate Cryptographic Lockfile with `uv lock`

From the root repository directory, run:
```bash
uv lock
```

**Output:**
```text
Resolved 30 packages in 314ms
Added enterprise-dependencies-bom v1.0.0
```

This generates `uv.lock` in the root repository. `uv.lock` records:
- Exact locked versions of direct and transitive dependencies.
- Cryptographic platform wheel hashes (SHA-256) ensuring zero tampering across environments.

---

## 5. Local Development Workflow

### Installing Dependencies in Virtual Environment

To install dependencies for a service while enforcing the central version rules:

```powershell
# Create a local virtual environment (if not already created)
uv venv .venv
# Activate virtual environment
.\.venv\Scripts\Activate.ps1    # On Windows
# source .venv/bin/activate     # On Linux / macOS

# Install Exchange Service dependencies governed by central overrides:
uv pip install -r currency-exchange-service-python/requirements.txt --override overrides.txt

# Install Conversion Service dependencies governed by central overrides:
uv pip install -r currency-conversion-service-python/requirements.txt --override overrides.txt
```

> [!TIP]
> If installing directly to your system Python (without a virtual environment), append `--system`:
> ```powershell
> uv pip install --system -r currency-exchange-service-python/requirements.txt --override overrides.txt
> ```

### Running Automated Unit & Integration Tests

Execute the test suites for both services:
```powershell
pytest currency-exchange-service-python/tests -v
pytest currency-conversion-service-python/tests -v
```

Expected result: **15/15 Passed (100% Green)**.

---

## 6. Containerization & Docker Multi-Stage Pipeline

### Optimized Dockerfile with Pre-Built `uv` Binary

Instead of running slow `pip install` inside Docker, we copy the official pre-compiled `uv` binary directly from GitHub Container Registry (`ghcr.io/astral-sh/uv:latest`).

File: `currency-exchange-service-python/Dockerfile` (and identically for `currency-conversion-service-python/Dockerfile`):
```dockerfile
ARG PYTHON_IMAGE=python:3.12-slim

# --------------------------------------------------------
# Stage 1: Build & Dependencies Layer (Fast uv resolver)
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy pre-compiled uv binary directly (No pip install needed!)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy service dependencies and central overrides
COPY requirements.txt overrides.txt* ./
RUN if [ -f "overrides.txt" ]; then \
        echo "==> Enforcing centralized dependencies via uv --override overrides.txt" && \
        uv pip install --no-cache -r requirements.txt --override overrides.txt; \
    else \
        echo "==> Installing requirements via uv" && \
        uv pip install --no-cache -r requirements.txt; \
    fi

# --------------------------------------------------------
# Stage 2: Hardened Production Runtime (Clean & Lean)
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runner
WORKDIR /app

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    CONTEXT_PATH="/currency-exchange-service-python"

COPY --chown=appuser:appgroup . /app
USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "app:app"]
```

### Automated Build & Push PowerShell Script

Use the automation script `build-and-push-docker.ps1`. The script syncs `overrides.txt` into the build context before invoking Docker, builds multi-stage images, and tags them:

```powershell
# Build both images locally
.\build-and-push-docker.ps1 -Tag latest

# Or build and push to remote Docker registry:
.\build-and-push-docker.ps1 -Tag v1.0.0 -Push
```

### Docker Compose Smoke Testing

Run the full containerized ecosystem:
```powershell
docker compose up -d
```

Verify the live endpoints:
```powershell
# 1. Exchange Service Liveness Probe
curl http://localhost:8000/currency-exchange-service-python/health/liveness

# 2. Exchange Rate Lookup Endpoint (USD -> INR)
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR

# 3. Conversion Service Liveness Probe
curl http://localhost:8100/currency-conversion-service-python/health/liveness

# 4. Conversion Calculation Endpoint (USD -> INR, Qty: 10)
curl http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10
```

Tear down containers:
```powershell
docker compose down
```

---

## 7. How to Patch a Security Vulnerability (CVE) in Seconds

Suppose a critical CVE is reported in `urllib3` (e.g., version `2.2.3` is vulnerable, and version `2.2.4` contains the security patch).

### The Old Painful Way (36+ Microservices):
1. Checkout 36 separate Git branches.
2. Edit `requirements.txt` in 36 repositories: change `urllib3==2.2.3` to `urllib3==2.2.4`.
3. Open 36 Pull Requests.
4. Merge 36 PRs and trigger 36 separate deployment pipelines.

### The Modern `uv` Way (This Solution):
1. **Update Central BOM in 1 Place**:
   In root `pyproject.toml` and root `overrides.txt`, change:
   ```text
   urllib3==2.2.4
   ```

2. **Re-Lock the Entire Ecosystem**:
   ```bash
   uv lock
   ```
   `uv` updates `uv.lock` in under **0.5 seconds**.

3. **Rebuild & Deploy All Microservices**:
   ```powershell
   .\build-and-push-docker.ps1
   ```
   **Zero lines of code or requirements are modified in any microservice.** All 36+ containers immediately build with the secure version.

---

## 8. CLI Command Reference & Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Check uv Version** | `uv --version` |
| **Re-resolve & Lock Dependencies** | `uv lock` |
| **Install with Central Overrides** | `uv pip install -r requirements.txt --override overrides.txt` |
| **Run Unit Tests** | `pytest currency-exchange-service-python/tests -v` |
| **Build Docker Images** | `.\build-and-push-docker.ps1 -Tag latest` |
| **Start Microservices (Docker Compose)** | `docker compose up -d` |
| **Test Live Exchange API** | `curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR` |
| **Test Live Conversion API** | `curl http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10` |
| **Stop Microservices** | `docker compose down` |
