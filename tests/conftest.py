"""Shared test fixtures and environment setup."""

import os

# Set required env vars at import time so module-level app instantiation works.
# These are test-only values; never use in production.
_TEST_ENV = {
    "JWT_SECRET_KEY": "test-jwt-secret-key-for-unit-tests-only",
    "API_KEY_PEPPER": "test-api-key-pepper-only",
    "APP_ENV": "development",
}
for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)
