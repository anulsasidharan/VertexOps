"""Unit tests for backend.core.config."""

import os

import pytest
from pydantic import ValidationError

from backend.core.config import Settings, get_settings


def _base(**overrides):
    """Return minimal valid init kwargs (lowercase field names) for Settings."""
    return {
        "jwt_secret_key": "test-secret",
        "api_key_pepper": "test-pepper",
        **overrides,
    }


class TestSettingsDefaults:
    def test_loads_with_required_secrets(self):
        s = Settings(**_base())
        assert s.app_env == "development"
        assert s.debug is False
        assert s.jwt_algorithm == "HS256"

    def test_jwt_secret_exposed_as_secret_str(self):
        s = Settings(**_base())
        assert str(s.jwt_secret_key) != "test-secret"
        assert s.jwt_secret_key.get_secret_value() == "test-secret"

    def test_api_key_pepper_is_secret(self):
        s = Settings(**_base())
        assert s.api_key_pepper.get_secret_value() == "test-pepper"

    def test_cors_origins_default(self):
        s = Settings(**_base())
        assert "http://localhost:3000" in s.cors_origins

    def test_cors_origins_parsed_from_comma_string(self):
        s = Settings(**_base(cors_origins="http://a.com,http://b.com"))
        assert s.cors_origins == ["http://a.com", "http://b.com"]

    def test_is_development_property(self):
        s = Settings(**_base(app_env="development"))
        assert s.is_development is True
        assert s.is_production is False

    def test_is_production_property(self):
        s = Settings(**_base(app_env="production", openai_api_key="sk-test", debug=False))
        assert s.is_production is True
        assert s.is_development is False


class TestSettingsValidation:
    def test_missing_jwt_secret_raises(self, monkeypatch):
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        with pytest.raises(ValidationError, match="jwt_secret_key"):
            Settings(api_key_pepper="pepper")

    def test_missing_api_key_pepper_raises(self, monkeypatch):
        monkeypatch.delenv("API_KEY_PEPPER", raising=False)
        with pytest.raises(ValidationError, match="api_key_pepper"):
            Settings(jwt_secret_key="secret")

    def test_invalid_app_env_raises(self):
        with pytest.raises(ValidationError):
            Settings(**_base(app_env="invalid_env"))

    def test_invalid_log_level_raises(self):
        with pytest.raises(ValidationError):
            Settings(**_base(log_level="VERBOSE"))

    def test_production_requires_llm_provider(self):
        with pytest.raises(ValidationError, match="OPENAI_API_KEY or GCP_PROJECT_ID"):
            Settings(**_base(app_env="production", debug=False))

    def test_production_debug_true_raises(self):
        with pytest.raises(ValidationError, match="DEBUG must be False"):
            Settings(**_base(app_env="production", openai_api_key="sk-x", debug=True))

    def test_production_with_openai_key_passes(self):
        s = Settings(**_base(app_env="production", openai_api_key="sk-test", debug=False))
        assert s.is_production


class TestGetSettings:
    def test_get_settings_returns_same_instance(self):
        get_settings.cache_clear()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
        get_settings.cache_clear()
