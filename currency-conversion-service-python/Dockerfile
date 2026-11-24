# ========================================================
# Dockerfile: Currency Conversion Service (Python / Flask)
# Runtime: Python 3.15.2 / Python 3.12-slim Multi-Stage Build
# Context Path: /currency-conversion-service-python
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

ARG CONSTRAINT_URL=""

COPY requirements.txt constraints.txt* ./
RUN pip install --upgrade pip && \
    if [ -f "constraints.txt" ]; then \
        echo "==> Enforcing centralized constraints from local constraints.txt" && \
        pip install --no-cache-dir -r requirements.txt -c constraints.txt; \
    elif [ -n "$CONSTRAINT_URL" ]; then \
        echo "==> Enforcing centralized constraints from remote URL: $CONSTRAINT_URL" && \
        pip install --no-cache-dir -r requirements.txt -c "$CONSTRAINT_URL"; \
    else \
        echo "==> Installing requirements without constraints" && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# --------------------------------------------------------
# Stage 2: Hardened Production Runtime
# --------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runner

LABEL maintainer="Antigravity Multi-Agent System"
LABEL service="currency-conversion-service-python"
LABEL context_path="/currency-conversion-service-python"
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
    PORT=8100 \
    CONTEXT_PATH="/currency-conversion-service-python" \
    EXCHANGE_SERVICE_URL="http://currency-exchange-service-python:8000/currency-exchange-service-python"

# Copy application source
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8100

# Container health probe mounted under context path
HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/currency-conversion-service-python/health/liveness')" || exit 1

# Production WSGI server pointing to app:app
CMD ["gunicorn", "--bind", "0.0.0.0:8100", "--workers", "2", "--threads", "4", "--timeout", "60", "--access-logfile", "-", "app:app"]
