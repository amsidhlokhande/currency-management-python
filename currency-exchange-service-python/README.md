# Currency Exchange Service (`currency-exchange-service-python`)

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://palletsprojects.com/p/flask/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-Docker_Build_%26_Push-orange.svg)](.github/workflows/docker-build.yml)

Production-ready Currency Exchange Microservice built with Python and Flask. It leverages the shared **`enterprise-core-python`** enterprise library for standardized cross-cutting concerns (centralized exception handling, structured JSON logging with PII masking, latency interceptors, Spring Boot-style actuators, and Swagger UI).

---

## Table of Contents

- [Architecture & Key Features](#architecture--key-features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
  - [1. Clone Repository & Setup Virtual Environment](#1-clone-repository--setup-virtual-environment)
  - [2. Install Dependencies with `enterprise-core-python` v1.0.0](#2-install-dependencies-with-enterprise-core-python-v100)
  - [3. Environment Configuration](#3-environment-configuration)
  - [4. Run Application Locally](#4-run-application-locally)
  - [5. Run Unit & Integration Tests](#5-run-unit--integration-tests)
- [Docker Build & Push (Local)](#docker-build--push-local)
  - [1. Building Docker Image with Tag v1.0.0](#1-building-docker-image-with-tag-v100)
  - [2. Running the Docker Container](#2-running-the-docker-container)
  - [3. Pushing Docker Image to Docker Hub](#3-pushing-docker-image-to-docker-hub)
- [GitHub Actions CI/CD Workflow Setup](#github-actions-cicd-workflow-setup)
  - [1. Configure GitHub Secrets](#1-configure-github-secrets)
  - [2. Workflow Pipeline Details](#2-workflow-pipeline-details)
  - [3. Trigger Build & Push](#3-trigger-build--push)
- [API Endpoints Reference](#api-endpoints-reference)
- [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Architecture & Key Features

- **Base Context Path**: All business endpoints, actuators, and docs are mounted strictly under `/currency-exchange-service-python`.
- **Enterprise Core Integration (`v1.0.0`)**: Centralizes dependencies (Flask, Gunicorn, Waitress, Requests, Pytest) and enterprise utilities.
- **Dual Data Source Ingestion**: Loads exchange rates from local CSV (`data/exchange_rates.csv` or `C:\rates\exchange_rates.csv`) or AWS S3.
- **Resilient Multi-Stage Dockerfile**: Slim, hardened non-root container (`appuser:10001`) with multi-stage build caching.
- **Automated CI/CD**: Seamless GitHub Actions workflow to build, tag, and publish Docker images.

---

## Prerequisites

- **Python**: `3.10` or higher (`3.12` recommended)
- **Docker**: Docker Desktop or Docker Engine `20.10+` with Buildx
- **Git**: Git installed and configured locally
- **Docker Hub Account**: Required for pushing Docker images
- **GitHub Personal Access Token (PAT)** *(Only required if `enterprise-core-python` is private)*: Token with `repo:read` scope.

---

## Project Structure

```text
currency-exchange-service-python/
├── .github/
│   └── workflows/
│       └── docker-build.yml       # GitHub Actions CI/CD build & push pipeline
├── data/
│   └── exchange_rates.csv         # Default fallback currency exchange rates
├── e2e/
│   ├── entity/                    # Currency exchange data models
│   ├── exception/                 # Error definitions & handlers
│   ├── repository/                # CSV and AWS S3 rate loaders
│   ├── route/                     # Flask blueprints (exchange, actuator, swagger)
│   ├── service/                   # Business logic and rate lookup service
│   └── utils/                     # Interceptors and logging configuration
├── tests/
│   └── test_exchange_service.py   # Unit & API test suite
├── app.py                         # Application bootstrap and factory
├── constants.py                   # Environment and application constants
├── Dockerfile                     # Multi-stage hardened production Dockerfile
├── requirements.txt               # Dependencies with enterprise-core-python tag v1.0.0
└── README.md                      # Project documentation
```

---

## Local Development Setup

### 1. Clone Repository & Setup Virtual Environment

```bash
# Clone repository
git clone https://github.com/amsidhlokhande/currency-exchange-service-python.git
cd currency-exchange-service-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies with `enterprise-core-python` v1.0.0

The `requirements.txt` file references the exact tag `v1.0.0`:

```txt
enterprise-core-python @ git+https://github.com/amsidhlokhande/enterprise-core-python.git@v1.0.0
boto3
```

#### If `enterprise-core-python` is Public:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### If `enterprise-core-python` is Private:
Set your GitHub Personal Access Token (`GITHUB_TOKEN`):

**PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_personal_access_token_here"
pip install --upgrade pip
pip install "enterprise-core-python @ git+https://${env:GITHUB_TOKEN}@github.com/amsidhlokhande/enterprise-core-python.git@v1.0.0"
pip install -r requirements.txt
```

**Bash / Linux / macOS:**
```bash
export GITHUB_TOKEN="your_personal_access_token_here"
pip install --upgrade pip
pip install "enterprise-core-python @ git+https://${GITHUB_TOKEN}@github.com/amsidhlokhande/enterprise-core-python.git@v1.0.0"
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root to override default constants if needed:

```properties
SERVICE_NAME=currency-exchange-service-python
PORT=8000
ENV=development
LOG_LEVEL=INFO
CONTEXT_PATH=/currency-exchange-service-python

# Optional S3 / CSV rate configuration
RATES_CSV_PATH=data/exchange_rates.csv
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
```

### 4. Run Application Locally

```bash
python app.py
```

The application will start on port `8000`:
- **Context Path**: `http://localhost:8000/currency-exchange-service-python`
- **Health Actuator**: `http://localhost:8000/currency-exchange-service-python/actuator/health`
- **Swagger Documentation**: `http://localhost:8000/currency-exchange-service-python/swagger`

### 5. Run Unit & Integration Tests

```bash
pytest tests/ -v
```

---

## Docker Build & Push (Local)

The service includes a multi-stage `Dockerfile` that installs `git` in the builder stage to clone and install `enterprise-core-python` tag `v1.0.0`.

### 1. Building Docker Image with Tag v1.0.0

Replace `<DOCKER_USERNAME>` with your Docker Hub username.

#### Case A: If `enterprise-core-python` is Public
```powershell
docker build `
  -t <DOCKER_USERNAME>/currency-exchange-service-python:v1.0.0 `
  -t <DOCKER_USERNAME>/currency-exchange-service-python:latest .
```

#### Case B: If `enterprise-core-python` is Private
Pass your GitHub PAT using the `--build-arg GITHUB_TOKEN`:
```powershell
docker build `
  --build-arg GITHUB_TOKEN="<YOUR_GITHUB_PAT>" `
  -t <DOCKER_USERNAME>/currency-exchange-service-python:v1.0.0 `
  -t <DOCKER_USERNAME>/currency-exchange-service-python:latest .
```

> [!TIP]
> The `Dockerfile` uses `git config url.insteadOf` during the build stage when `GITHUB_TOKEN` is supplied, keeping the token out of the runtime container.

### 2. Running the Docker Container

#### Option A: Running Standalone
```powershell
docker run --rm -p 8000:8000 --name currency-exchange-service <DOCKER_USERNAME>/currency-exchange-service-python:latest
```

#### Option B: Running in a Shared Bridge Network (Communicating with `currency-conversion-service-python`)

In Docker, separate containers cannot reach each other via `localhost` because each container has its own isolated loopback network namespace. To enable inter-service communication:

1. **Create a shared user-defined Docker bridge network**:
   ```powershell
   docker network create currency-network
   ```

2. **Run `currency-exchange-service` attached to the network**:
   ```powershell
   docker run -d --rm `
     --name currency-exchange-service `
     --network currency-network `
     -p 8000:8000 `
     <DOCKER_USERNAME>/currency-exchange-service-python:latest
   ```

> [!TIP]
> - **From other containers on `currency-network`** (e.g. `currency-conversion-service-python`): This service is reachable at `http://currency-exchange-service:8000/currency-exchange-service-python` through Docker's built-in DNS service discovery.
> - **From your host machine**: This service is reachable at `http://localhost:8000/currency-exchange-service-python` via the mapped port `-p 8000:8000`.

#### Verify Container Health & Endpoints
Verify in another terminal or browser:
```powershell
# Check health actuator
curl http://localhost:8000/currency-exchange-service-python/actuator/health

# Query exchange rate
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR
```

Stop the container:
```powershell
docker stop currency-exchange-service
```

### 3. Pushing Docker Image to Docker Hub

```powershell
# 1. Login to Docker Hub
docker login

# 2. Push both version tag and latest tag
docker push <DOCKER_USERNAME>/currency-exchange-service-python:v1.0.0
docker push <DOCKER_USERNAME>/currency-exchange-service-python:latest
```

---

## GitHub Actions CI/CD Workflow Setup

The repository includes a ready-to-run GitHub Actions workflow in [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml) that automatically builds the Docker image and pushes it to Docker Hub on every push to branch `main` or manual trigger.

### 1. Configure GitHub Secrets

Navigate to your GitHub repository: **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.

Add the following repository secrets:

| Secret Name | Required | Description |
| :--- | :---: | :--- |
| `READ_PACKAGES_TOKEN` | **Yes** / *Recommended* | GitHub Personal Access Token (PAT) with `repo` permission to clone private dependencies such as `enterprise-core-python`. |
| `DOCKER_USERNAME` | **Yes** | Your Docker Hub account username. |
| `DOCKER_PASSWORD` | **Yes** | Your Docker Hub Personal Access Token (PAT) or password. |

> [!NOTE]
> `READ_PACKAGES_TOKEN` is passed as the `GITHUB_TOKEN` build argument into Docker to securely authenticate cloning private Git repositories. If not set, it defaults to the workflow's `${{ secrets.GITHUB_TOKEN }}`.

### 2. Workflow Pipeline Details

Below is the workflow configuration located at `.github/workflows/docker-build.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    env:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    steps:
      - name: Checkout Microservice Code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Log in to Docker Hub if secrets are configured
      - name: Log in to Docker Registry
        if: ${{ env.DOCKER_USERNAME != '' && env.DOCKER_PASSWORD != '' }}
        uses: docker/login-action@v3
        with:
          username: ${{ env.DOCKER_USERNAME }}
          password: ${{ env.DOCKER_PASSWORD }}

      # Build & Push Docker image
      - name: Build and Push Docker Image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: ${{ env.DOCKER_USERNAME != '' && env.DOCKER_PASSWORD != '' }}
          tags: ${{ env.DOCKER_USERNAME || 'local' }}/${{ github.event.repository.name || 'currency-exchange-service-python' }}:latest
          build-args: |
            GITHUB_TOKEN=${{ secrets.READ_PACKAGES_TOKEN || secrets.GITHUB_TOKEN }}
```

### 3. Trigger Build & Push

1. **Commit and push** your changes to the `main` branch:
   ```bash
   git add requirements.txt Dockerfile .github/workflows/docker-build.yml README.md
   git commit -m "build: configure enterprise-core-python v1.0.0 tag and docker workflow"
   git push origin main
   ```
2. Or trigger manually under **Actions** > **Build and Push Docker Image** > **Run workflow**.

---

## API Endpoints Reference

All endpoints are prefixed with `/currency-exchange-service-python`:

### Business Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/currency-exchange/from/{from}/to/{to}` | Get live exchange rate for a currency pair (e.g. `USD` to `INR`). |
| `GET` | `/currency-exchange/rates` | List all supported currency rates in catalog. |
| `POST` | `/currency-exchange/reload` | Hot-reload exchange rates from S3 or local CSV. |

#### Example Request & Response
```bash
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR
```
```json
{
  "from": "USD",
  "to": "INR",
  "conversionMultiple": 83.5,
  "environment": "8000 development"
}
```

### Operational Actuators & Docs

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/actuator/health` | Comprehensive application health probe. |
| `GET` | `/actuator/health/liveness` | Kubernetes liveness probe (`{"status": "UP"}`). |
| `GET` | `/actuator/health/readiness` | Kubernetes readiness probe (verifies rate data loaded). |
| `GET` | `/actuator/info` | Service metadata, name, and version. |
| `GET` | `/actuator/metrics` | System, memory, and process metrics. |
| `GET` | `/swagger` | Interactive Swagger UI documentation. |
| `GET` | `/swagger/openapi.json` | Raw OpenAPI 3.0 specification. |

---

## Troubleshooting & FAQ

### 1. `fatal: could not read Username for 'https://github.com': No such device or address`
- **Cause**: Pip inside Docker or local terminal is trying to clone a private repository without authentication.
- **Fix**: Provide your GitHub Personal Access Token with `repo:read` scope as `--build-arg GITHUB_TOKEN="..."` (Docker) or `git+https://${GITHUB_TOKEN}@github.com/...` (local pip).

### 2. Slow Docker Build during `apt-get`
- The `Dockerfile` builder stage only installs minimal `git` and cleans up `/var/lib/apt/lists/*` to keep builds fast and lightweight. Ensure Docker Desktop has internet connectivity.

### 3. Updating to a New Version of `enterprise-core-python`
- Update the tag reference in `requirements.txt`:
  ```txt
  enterprise-core-python @ git+https://github.com/amsidhlokhande/enterprise-core-python.git@v1.1.0
  ```
- Rebuild Docker image or push to GitHub to trigger CI/CD.
