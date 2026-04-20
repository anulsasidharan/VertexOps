# =============================================================================
# Stage 1: export locked requirements (uv) + build wheels
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Build tools needed for native wheels (asyncpg, bcrypt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pin the uv image tag for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-annotate -o requirements.txt

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# =============================================================================
# Stage 2: runtime base — shared by api and worker targets
# =============================================================================
FROM python:3.11-slim AS runtime-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Non-root user for production hardening
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home --shell /sbin/nologin appuser

WORKDIR /app

# Runtime system libs only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pre-built wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels
COPY --from=builder /build/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels -r /tmp/requirements.txt \
    && rm -rf /tmp/wheels /tmp/requirements.txt

# Copy application source
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY scripts/ ./scripts/

RUN chown -R appuser:appgroup /app
USER appuser

# =============================================================================
# Stage 3a: api — FastAPI + Uvicorn
# =============================================================================
FROM runtime-base AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage 3b: worker — Celery background task processor
# =============================================================================
FROM runtime-base AS worker

HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=3 \
    CMD celery -A backend.workers.celery_app inspect ping -d "celery@$(hostname)" --timeout 10 || exit 1

CMD ["celery", "-A", "backend.workers.celery_app", "worker", \
     "--loglevel=info", \
     "--queues=ingest,embed,eval,index", \
     "--concurrency=2", \
     "--max-tasks-per-child=100"]

# =============================================================================
# Stage 4: frontend-builder — install deps and build the React/Vite SPA
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts

COPY frontend/ .
# VITE_API_BASE_URL is intentionally unset — Nginx proxies /api → api:8000
RUN npm run build

# =============================================================================
# Stage 5: frontend — Nginx serves static SPA and reverse-proxies /api
# =============================================================================
FROM nginx:1.27-alpine AS frontend

COPY --from=frontend-builder /build/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1
