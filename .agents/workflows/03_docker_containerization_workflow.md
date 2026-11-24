# 📋 Workflow 3: Docker & Containerization Workflow

## 1. Overview & Objective
Governed by **Agent 3 (DevOps & Containerization Specialist)**. This workflow defines the multi-stage build strategy, non-root user security hardening, health probes mounted under each service's context path, and root Docker Compose orchestration.

---

## 2. Step-by-Step Execution Sequence

### Step 3.1: Context Path Enforced Healthchecks
1. **Exchange Service**:
   - `CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/currency-exchange-service-python/health/liveness')"`
2. **Conversion Service**:
   - `CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/currency-conversion-service-python/health/liveness')"`

### Step 3.2: WSGI Gunicorn Execution
Both containers execute `app:app` via Gunicorn with 2 workers and 4 threads.

### Step 3.3: Docker Compose Mesh
Services interact over `currency-mesh` with `EXCHANGE_SERVICE_URL="http://currency-exchange-service-python:8000/currency-exchange-service-python"`.
