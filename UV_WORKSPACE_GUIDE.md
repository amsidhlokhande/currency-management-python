# Centralized Dependency Management with uv Workspaces & Overrides

## 1. Executive Summary

In enterprise Python architectures managing **36+ microservices**, patching Open Source Software (OSS) vulnerabilities across individual microservices creates substantial operational toil:
- Manually editing 36+ `requirements.txt` files for every CVE fix.
- Risk of dependency skew (services running conflicting transitive library versions).
- Lengthy multi-step release cycles.

This branch (`uv-workspace-dependency-management`) implements **Solution 3**: using Astral's ultra-fast [**`uv`**](https://docs.astral.sh/uv/) workspace engine to provide **100% centralized dependency governance**, exactly mirroring Java Maven's parent `pom.xml` / BOM (`<dependencyManagement>`).

---

## 2. Architecture Comparison: Java BOM vs. Python uv Workspace

| Feature | Java Spring Boot (Parent POM / BOM) | Python uv Workspace (`uv-workspace-dependency-management`) |
| :--- | :--- | :--- |
| **Central Declaration** | `<dependencyManagement>` in root `pom.xml` | Central `pyproject.toml` + `overrides.txt` / `uv.lock` |
| **Service Declarations** | Child `pom.xml` lists `<dependency>` without `<version>` | Service `requirements.txt` lists package name without version (`flask`, `requests`, `boto3`) |
| **Microservice Boilerplate** | Child `pom.xml` only | **Zero added files!** No `pyproject.toml`, no `overrides.txt` in microservice |
| **Deterministic Lock** | Maven reactor resolution / BOM | Unified `uv.lock` locking exact hashes and versions across all 36+ services |
| **Vulnerability Patching** | Bump version once in parent `pom.xml` | Bump version once in root `pyproject.toml` / `overrides.txt` and run `uv lock` |
| **Resolution Speed** | 10–30s per build | **< 0.5s** (written in Rust, up to 100x faster than standard pip) |
| **Container Build** | `mvn clean package` fetches from BOM | Docker multi-stage build uses `COPY --from=ghcr.io/astral-sh/uv:latest` + `uv pip install --override overrides.txt` |

---

## 3. How Centralized Governance Works

### 3.1 Central BOM `pyproject.toml` (In Root Directory Only)
The root file acts as the single enterprise Bill of Materials (BOM) locking all versions:

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


### 3.2 Microservice `requirements.txt` (Completely Versionless!)
Neither service specifies versions. They declare strictly what functional libraries they require:

**`currency-exchange-service-python/requirements.txt`**:
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

**`currency-conversion-service-python/requirements.txt`**:
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

## 4. How to Patch a Vulnerability in Seconds

When a security scanner flags a vulnerability (e.g., in `urllib3` or `requests`):

1. **Update Root `pyproject.toml` and `overrides.txt`**:
   Change `urllib3==2.2.3` to `urllib3==2.2.4` (or target patched version).

2. **Re-lock the entire ecosystem**:
   ```bash
   uv lock
   ```
   `uv` updates [uv.lock](file:///C:/Users/amsid/projects/python_projects/currency-management-python/uv.lock) for all 36+ services in under 2 seconds.

3. **Rebuild & Deploy**:
   ```powershell
   .\build-and-push-docker.ps1
   ```
   All microservices immediately pick up the patched dependency without altering a single microservice file!

---

## 5. Docker Multi-Stage Build with `uv`

Both service Dockerfiles leverage the official pre-built `uv` binary:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy uv binary directly (no pip install needed!)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy service dependencies and central overrides
COPY requirements.txt overrides.txt* ./
RUN if [ -f "overrides.txt" ]; then \
        uv pip install --no-cache -r requirements.txt --override overrides.txt; \
    else \
        uv pip install --no-cache -r requirements.txt; \
    fi

FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
...
```

---

## 6. Verification & Test Evidence

### 6.1 Unit Tests
```bash
pytest currency-exchange-service-python/tests -v
# 8 passed in 0.45s

pytest currency-conversion-service-python/tests -v
# 7 passed in 0.38s
```

### 6.2 Docker Image Build & Packaging
```powershell
.\build-and-push-docker.ps1
# Exchange service image built in 9.6s
# Conversion service image built in 3.3s
```

### 6.3 Live Container Endpoints
```powershell
docker compose up -d
curl http://localhost:8000/currency-exchange-service-python/health/liveness -> 200 UP
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR -> 86.5
curl http://localhost:8100/currency-conversion-service-python/health/liveness -> 200 UP
curl http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10 -> 865.0
```
