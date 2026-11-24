# ========================================================
# Dockerfile: Currency Exchange Service (Python / Flask)
# Runtime: Python 3.15.2 / Python 3.12-slim Multi-Stage Build
# Context Path: /currency-exchange-service-python
# ========================================================

ARG PYTHON_IMAGE=python:3.12-slim

# --------------------------------------------------------
# Stage 1: Build & Dependencies Layer
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependencies and internal enterprise shared library wheel
COPY requirements.txt enterprise_core_python-*.whl* ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --find-links . -r requirements.txt

# --------------------------------------------------------
# Stage 2: Hardened Production Runtime
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runner

LABEL maintainer="Antigravity Multi-Agent System"
LABEL service="currency-exchange-service-python"
LABEL context_path="/currency-exchange-service-python"
LABEL version="1.0.0"

WORKDIR /app

# Security: Create unprivileged non-root user (appuser: UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Copy isolated virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    CONTEXT_PATH="/currency-exchange-service-python" \
    RATES_CSV_PATH="data/exchange_rates.csv"

# Copy application source
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8000

# Container health probe mounted under context path
HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/currency-exchange-service-python/health/liveness')" || exit 1

# Production WSGI server pointing to app:app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60", "--access-logfile", "-", "app:app"]
