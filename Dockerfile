# Stage 1: Build virtualenv with all compiled dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Native toolchain for packages requiring C extension builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Keep isolated dependencies inside /opt/venv for clean multi-stage transfer
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 2: Lean production runtime
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production

# Lightweight curl binary required by container health probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

# Enforce least-privilege security policy (non-root execution)
RUN groupadd -g 1000 finguard && \
    useradd -u 1000 -g finguard -s /bin/bash -m finguard

COPY --chown=finguard:finguard src/ /app/src/
COPY --chown=finguard:finguard pyproject.toml README.md /app/

# Install local package into venv without re-fetching pinned dependencies
RUN pip install --no-cache-dir --no-deps . && \
    chown -R finguard:finguard /opt/venv /app

USER finguard

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]