#!/usr/bin/env bash
# Run the VertexOps test suite locally.
#
# Usage:
#   ./scripts/run-tests.sh              # unit tests only (default)
#   ./scripts/run-tests.sh --all        # unit + integration (requires live DB + Redis)
#   ./scripts/run-tests.sh --coverage   # unit tests with coverage report
#   ./scripts/run-tests.sh --lint       # lint only

set -euo pipefail

UNIT_ONLY=true
COVERAGE=false
LINT=false

for arg in "$@"; do
  case "$arg" in
    --all)      UNIT_ONLY=false ;;
    --coverage) COVERAGE=true ;;
    --lint)     LINT=true; UNIT_ONLY=false ;;
  esac
done

# Ensure required env vars have fallbacks for local runs
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-local-dev-secret-for-tests}"
export API_KEY_PEPPER="${API_KEY_PEPPER:-local-dev-pepper-for-tests}"

if [[ "${LINT}" == "true" ]]; then
  echo "==> ruff check"
  uv run ruff check .
  echo "==> ruff format check"
  uv run ruff format --check .
  echo "==> mypy"
  uv run mypy backend/ --ignore-missing-imports || true
  exit 0
fi

PYTEST_ARGS=(-v --tb=short)

if [[ "${COVERAGE}" == "true" ]]; then
  PYTEST_ARGS+=(--cov=backend --cov-report=term-missing --cov-report=html:htmlcov)
fi

if [[ "${UNIT_ONLY}" == "true" ]]; then
  echo "==> Running unit tests..."
  uv run pytest tests/unit/ "${PYTEST_ARGS[@]}"
else
  echo "==> Running all tests (requires live PostgreSQL and Redis)..."
  uv run pytest tests/ "${PYTEST_ARGS[@]}"
fi
