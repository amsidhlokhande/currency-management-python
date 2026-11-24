# 📘 Approach 1: Centralized Constraint Dependency Management (`pip -c constraints.txt` BOM)

> **Branch**: `centralized-constraint-dependency`  
> **Target Audience**: Solution Architects, Security Engineers, Tech Leads, and Backend Developers  
> **Java Analogy**: Maven Parent BOM with `<dependencyManagement>` (Bill of Materials)

---

## 📑 Table of Contents
1. [Problem Statement & Enterprise Motivation](#1-problem-statement--enterprise-motivation)
2. [Architectural Concept & Comparison to Java Maven](#2-architectural-concept--comparison-to-java-maven)
3. [Understanding pip Constraints (`-c`) vs. Requirements (`-r`)](#3-understanding-pip-constraints--c-vs-requirements--r)
4. [Step-by-Step Implementation Guide](#4-step-by-step-implementation-guide)
   - [Step 4.1: Create the Central Enterprise BOM (`constraints.txt`)](#step-41-create-the-central-enterprise-bom-constraintstxt)
   - [Step 4.2: Strip Hardcoded Versions from Microservice `requirements.txt`](#step-42-strip-hardcoded-versions-from-microservice-requirementstxt)
   - [Step 4.3: Install Dependencies Locally Using Constraint Flag](#step-43-install-dependencies-locally-using-constraint-flag)
   - [Step 4.4: Enforce Global Constraints via Environment Variable (`PIP_CONSTRAINT`)](#step-44-enforce-global-constraints-via-environment-variable-pip_constraint)
5. [Enterprise Distribution Patterns for 36+ Separate Repositories](#5-enterprise-distribution-patterns-for-36-separate-repositories)
   - [Pattern A: Hosted HTTP URL (GitHub / GitLab / Bitbucket Raw URL)](#pattern-a-hosted-http-url-github--gitlab--bitbucket-raw-url)
   - [Pattern B: Enterprise Artifact Repository (JFrog Artifactory / Nexus / S3)](#pattern-b-enterprise-artifact-repository-jfrog-artifactory--nexus--s3)
   - [Pattern C: CI/CD Pipeline Global Injection](#pattern-c-cicd-pipeline-global-injection)
6. [Containerization & Docker Multi-Stage Pipeline](#6-containerization--docker-multi-stage-pipeline)
   - [Production-Grade Dockerfile with Constraints](#production-grade-dockerfile-with-constraints)
   - [Automated Build & Push PowerShell Script](#automated-build--push-powershell-script)
   - [Docker Compose Smoke Testing](#docker-compose-smoke-testing)
7. [How to Patch a Security Vulnerability (CVE) in Seconds](#7-how-to-patch-a-security-vulnerability-cve-in-seconds)
8. [CLI Command Reference & Cheat Sheet](#8-cli-command-reference--cheat-sheet)

---

## 1. Problem Statement & Enterprise Motivation

In organizations with **36+ Python microservices**, every microservice historically manages its own `requirements.txt` with hardcoded library versions:
- `currency-exchange-service-python` has `urllib3==2.2.1`.
- `currency-conversion-service-python` has `urllib3==2.1.0`.
- 34 other microservices have varied versions (`urllib3==1.26.18`, `2.0.7`, etc.).

### The Pain:
When an enterprise security scanner (such as Snyk, SonarQube, Prisma Cloud, or Mend) flags a critical vulnerability (CVE) in `urllib3`:
1. Developers must edit 36+ separate `requirements.txt` files.
2. 36+ Pull Requests must be authored, reviewed, and approved.
3. 36+ CI/CD pipelines must be triggered, built, tested, and deployed to production.
4. If a zero-day exploit emerges, coordinating 36 deployments can take days or weeks.

**The Solution**: A centralized Bill of Materials (BOM) file called `constraints.txt`. Microservices list **only** package names in `requirements.txt`, while all version locking and security patches are enforced globally through `pip install -c constraints.txt`.

---

## 2. Architectural Concept & Comparison to Java Maven

If you have worked with Java Spring Boot and Maven:

```
               JAVA SPRING BOOT (MAVEN)                                  PYTHON (PIP CONSTRAINTS BOM)
      ┌────────────────────────────────────────┐                ┌────────────────────────────────────────┐
      │             parent-pom.xml             │                │            constraints.txt             │
      │        <dependencyManagement>          │                │          (Central Enterprise BOM)      │
      │   - spring-boot-starter: 3.2.0         │                │   - Flask==3.1.0                       │
      │   - jackson-databind: 2.16.0           │                │   - requests==2.32.3                   │
      │   - urllib3/httpclient: 5.3.1          │                │   - urllib3==2.2.3                     │
      └──────────────────┬─────────────────────┘                └──────────────────┬─────────────────────┘
                         │                                                         │
         ┌───────────────┴───────────────┐                         ┌───────────────┴───────────────┐
         ▼                               ▼                         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐       ┌─────────────────┐             ┌─────────────────┐
│ Child Pom (SVC 1)│             │ Child Pom (SVC 2)│       │ requirements.txt│             │ requirements.txt│
│ <dependency>    │             │ <dependency>    │       │ (Exchange Svc)  │             │ (Conversion Svc)│
│  spring-starter │             │  spring-starter │       │ - Flask         │             │ - Flask         │
│  (NO VERSION)   │             │  (NO VERSION)   │       │ - boto3         │             │ - requests      │
└─────────────────┘             └─────────────────┘       │ (NO VERSIONS)   │             │ (NO VERSIONS)   │
                                                          └─────────────────┘             └─────────────────┘
```

| Dimension | Java Maven BOM Pattern | Python pip Constraints BOM Pattern |
| :--- | :--- | :--- |
| **Central Version Authority** | `<dependencyManagement>` in root `pom.xml` | `central-dependency-management/constraints.txt` |
| **Microservice Manifest** | `<dependency>` without `<version>` tag | `requirements.txt` without version pins |
| **Enforcement Mechanism** | Maven reactor reads parent BOM | `pip install -r requirements.txt -c constraints.txt` |
| **Selectivity** | Packages in BOM are only installed if child requests them | Packages in `constraints.txt` are only installed if `requirements.txt` requests them |
| **Zero Code Changes for CVE** | Bump version once in parent `pom.xml` | Bump version once in `constraints.txt` |

---

## 3. Understanding pip Constraints (`-c`) vs. Requirements (`-r`)

Many developers confuse **Requirements** (`-r`) with **Constraints** (`-c`):

| Feature | `requirements.txt` (`-r`) | `constraints.txt` (`-c`) |
| :--- | :--- | :--- |
| **Purpose** | Specifies **WHAT** packages a service needs to run. | Specifies **WHICH VERSION** to use IF a package is installed. |
| **Installation Behavior** | Installs every package listed in the file. | **Does NOT install** packages automatically. Only governs versions if requested by `-r`. |
| **Location** | Stored inside each microservice repository. | Stored centrally in a shared repo, internal URL, or Artifactory. |
| **Example Content** | `Flask`, `requests`, `boto3` | `Flask==3.1.0`, `requests==2.32.3`, `urllib3==2.2.3` |

> [!NOTE]
> Even if `constraints.txt` lists 100 enterprise libraries (e.g., `celery`, `redis`, `boto3`, `django`), a microservice that only requires `Flask` and `requests` will **only** install `Flask` and `requests`!

---

## 4. Step-by-Step Implementation Guide

### Step 4.1: Create the Central Enterprise BOM (`constraints.txt`)

Create a central directory `central-dependency-management/` containing `constraints.txt`. This file locks all direct and transitive dependencies to exact, security-vetted versions.

File: `central-dependency-management/constraints.txt`
```text
# Core Web Framework & WSGI
Flask==3.1.0
Werkzeug==3.1.3
gunicorn==23.0.0
waitress==3.0.1

# HTTP Clients & Network Security
requests==2.32.3
urllib3==2.2.3
certifi==2024.8.30
idna==3.10
charset-normalizer==3.4.0

# Cloud SDK & Storage
boto3==1.35.40
botocore==1.35.40
jmespath==1.0.1
s3transfer==0.10.3

# Observability & Structured Logging
python-json-logger==2.0.7

# Testing & Quality Assurance
pytest==8.3.3
iniconfig==2.0.0
packaging==24.1
pluggy==1.5.0
```

---

### Step 4.2: Strip Hardcoded Versions from Microservice `requirements.txt`

Remove all hardcoded version specifiers from each microservice's `requirements.txt`.

#### 1. Currency Exchange Service
File: `currency-exchange-service-python/requirements.txt`
```text
Flask
python-json-logger
boto3
pytest
gunicorn
waitress
requests
```

#### 2. Currency Conversion Service
File: `currency-conversion-service-python/requirements.txt`
```text
Flask
python-json-logger
pytest
gunicorn
waitress
requests
```

---

### Step 4.3: Install Dependencies Locally Using Constraint Flag

In your terminal or virtual environment, install dependencies by passing the central constraints file via the `-c` flag:

```powershell
# 1. Currency Exchange Service
pip install -r currency-exchange-service-python/requirements.txt -c central-dependency-management/constraints.txt

# 2. Currency Conversion Service
pip install -r currency-conversion-service-python/requirements.txt -c central-dependency-management/constraints.txt
```

Verify that the exact pinned versions were installed:
```powershell
pip show Flask urllib3 requests
# Shows:
# Name: Flask, Version: 3.1.0
# Name: urllib3, Version: 2.2.3
# Name: requests, Version: 2.32.3
```

---

### Step 4.4: Enforce Global Constraints via Environment Variable (`PIP_CONSTRAINT`)

`pip` natively supports an environment variable called `PIP_CONSTRAINT`. When this variable is set, pip **automatically enforces the constraint file on every single `pip install` command**, even if the developer forgets to type `-c`!

**On Windows (PowerShell):**
```powershell
$env:PIP_CONSTRAINT = "C:\Users\amsid\projects\python_projects\currency-management-python\central-dependency-management\constraints.txt"
# Now standard pip install uses constraints automatically:
pip install -r currency-exchange-service-python/requirements.txt
```

**On Linux / macOS / CI/CD (Bash):**
```bash
export PIP_CONSTRAINT="https://artifactory.company.internal/bom/constraints.txt"
pip install -r requirements.txt
```

---

## 5. Enterprise Distribution Patterns for 36+ Separate Repositories

If your 36+ microservices live in 36 separate Git repositories, use one of the following 3 battle-tested enterprise distribution patterns:

### Pattern A: Hosted HTTP URL (GitHub / GitLab / Bitbucket Raw URL)
Maintain `constraints.txt` in a dedicated central governance repository (e.g., `git@github.com:my-org/enterprise-python-bom.git`).
Microservices install dependencies directly via HTTP:
```bash
pip install -r requirements.txt -c https://raw.githubusercontent.com/my-org/enterprise-python-bom/main/constraints.txt
```

### Pattern B: Enterprise Artifact Repository (JFrog Artifactory / Nexus / S3)
Publish `constraints.txt` as a versioned artifact to JFrog Artifactory or an AWS S3 bucket during your release cycle:
```bash
pip install -r requirements.txt -c https://artifactory.company.internal/artifactory/generic-local/python-bom/constraints-v1.0.txt
```

### Pattern C: CI/CD Pipeline Global Injection
In your Jenkins, GitLab CI, GitHub Actions, or Azure DevOps base pipeline templates, inject the `PIP_CONSTRAINT` environment variable globally into all runner agents:
```yaml
# Example: GitHub Actions / GitLab CI Step
- name: Install Dependencies with Enterprise BOM
  env:
    PIP_CONSTRAINT: https://artifactory.company.internal/artifactory/generic-local/python-bom/constraints.txt
  run: |
    pip install -r requirements.txt
```

---

## 6. Containerization & Docker Multi-Stage Pipeline

### Production-Grade Dockerfile with Constraints

Both services use hardened multi-stage Docker builds:

File: `currency-exchange-service-python/Dockerfile`
```dockerfile
ARG PYTHON_IMAGE=python:3.12-slim

# --------------------------------------------------------
# Stage 1: Build & Dependencies Layer
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy service requirements and central constraints
COPY requirements.txt constraints.txt* ./
RUN if [ -f "constraints.txt" ]; then \
        echo "==> Enforcing centralized constraints (BOM)" && \
        pip install --no-cache-dir -r requirements.txt -c constraints.txt; \
    else \
        echo "==> Installing requirements" && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# --------------------------------------------------------
# Stage 2: Hardened Production Runtime (Clean & Lean)
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runner
WORKDIR /app

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

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

Use `build-and-push-docker.ps1` to sync `constraints.txt` into the build contexts and trigger multi-stage builds:
```powershell
.\build-and-push-docker.ps1 -Tag latest
```

### Docker Compose Smoke Testing

Run the containers and test endpoints:
```powershell
docker compose up -d

# 1. Test Exchange Service
curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR

# 2. Test Conversion Service
curl http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/10

docker compose down
```

---

## 7. How to Patch a Security Vulnerability (CVE) in Seconds

Suppose a high-severity vulnerability (CVE) is discovered in `urllib3` (e.g. `2.2.3` is vulnerable, and `2.2.4` contains the security patch).

### Step 1: Update Version in ONE Central File
Open `central-dependency-management/constraints.txt` (or update it in your central Git/Artifactory repo):
```text
# Change:
urllib3==2.2.3

# To:
urllib3==2.2.4
```

### Step 2: Push the Commit / Publish the File
```powershell
git commit -am "sec: patch urllib3 CVE by bumping to 2.2.4 in central BOM"
git push
```

### Step 3: Trigger Service Redeployment
Trigger your deployment pipeline (`.\build-and-push-docker.ps1`).

**Result**:
- **0 lines of code** were touched in `currency-exchange-service-python`.
- **0 lines of code** were touched in `currency-conversion-service-python`.
- **0 lines of code** were touched in any of your 36+ microservices.
- All 36+ containers immediately build and deploy with the secure `urllib3==2.2.4` version!

---

## 8. CLI Command Reference & Cheat Sheet

| Task | Command |
| :--- | :--- |
| **Install with Local Constraints** | `pip install -r requirements.txt -c central-dependency-management/constraints.txt` |
| **Install with Remote URL Constraints** | `pip install -r requirements.txt -c https://company.internal/constraints.txt` |
| **Set Environment Variable (Windows)** | `$env:PIP_CONSTRAINT = "path/to/constraints.txt"` |
| **Set Environment Variable (Linux/Mac)**| `export PIP_CONSTRAINT="https://company.internal/constraints.txt"` |
| **Verify Installed Package Versions** | `pip show Flask urllib3 requests` |
| **Run Unit Tests** | `pytest currency-exchange-service-python/tests -v` |
| **Build Docker Images** | `.\build-and-push-docker.ps1 -Tag latest` |
| **Start Containers** | `docker compose up -d` |
| **Test Live Exchange API** | `curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR` |
| **Stop Containers** | `docker compose down` |
