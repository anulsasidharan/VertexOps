# =============================================================================
# Stage 1: dependency builder
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools needed for some native wheels (e.g. asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# =============================================================================
# Stage 2: runtime image
# =============================================================================
FROM python:3.11-slim AS runtime

# Non-root user for production safety
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Runtime system libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pre-built wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels -r requirements.txt \
    && rm -rf /tmp/wheels requirements.txt

# Copy application source
COPY backend/ ./backend/
# alembic/ and alembic.ini are added in Task #5 (db-foundation);
# uncomment the lines below once that branch is merged.
# COPY alembic/ ./alembic/
# COPY alembic.ini ./alembic.ini

RUN chown -R appuser:appgroup /app
USER appuser

# Expose API port
EXPOSE 8000

# Health check — delegates to the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default: run the API server (override CMD for worker containers)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
