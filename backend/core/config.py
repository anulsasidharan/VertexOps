"""Application settings — typed configuration via pydantic-settings."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "VertexOps"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # -------------------------------------------------------------------------
    # Database (PostgreSQL)
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vertexops"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30

    # -------------------------------------------------------------------------
    # Redis (cache + Celery broker)
    # -------------------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"
    redis_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # -------------------------------------------------------------------------
    # Auth — required; no hardcoded defaults
    # -------------------------------------------------------------------------
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    api_key_pepper: SecretStr

    # -------------------------------------------------------------------------
    # LLM providers
    # -------------------------------------------------------------------------
    openai_api_key: Optional[SecretStr] = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_max_retries: int = 3

    # -------------------------------------------------------------------------
    # GCP / Vertex AI
    # -------------------------------------------------------------------------
    gcp_project_id: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    vertex_ai_embedding_model: str = "text-embedding-004"
    vertex_ai_chat_model: str = "gemini-1.5-flash"

    # -------------------------------------------------------------------------
    # Vector store (Pinecone)
    # -------------------------------------------------------------------------
    pinecone_api_key: Optional[SecretStr] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "vertexops-index"

    # -------------------------------------------------------------------------
    # Object storage
    # -------------------------------------------------------------------------
    storage_backend: Literal["local", "gcs"] = "local"
    gcs_bucket_name: Optional[str] = None
    storage_local_path: str = "./storage"

    # -------------------------------------------------------------------------
    # Rate limiting
    # -------------------------------------------------------------------------
    rate_limit_enabled: bool = True
    rate_limit_default_requests: int = 100
    rate_limit_default_window_seconds: int = 60
    rate_limit_strict_requests: int = 20
    rate_limit_strict_window_seconds: int = 60

    # -------------------------------------------------------------------------
    # Observability
    # -------------------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    metrics_enabled: bool = False
    mlflow_enabled: bool = False
    mlflow_tracking_uri: Optional[str] = None
    mlflow_experiment_name: str = "vertexops-evaluations"
    otel_exporter_otlp_endpoint: Optional[str] = None

    # -------------------------------------------------------------------------
    # Notifications (SendGrid / Twilio) — optional, feature-flagged
    # -------------------------------------------------------------------------
    notifications_enabled: bool = False
    notification_alert_emails: Optional[str] = None  # comma-separated operator inboxes
    notifications_sendgrid_enabled: bool = False
    sendgrid_api_key: Optional[SecretStr] = None
    sendgrid_from_email: Optional[str] = None
    notifications_twilio_enabled: bool = False
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[SecretStr] = None
    twilio_from_number: Optional[str] = None
    twilio_alert_to_number: Optional[str] = None

    # -------------------------------------------------------------------------
    # Billing / usage metering (Stripe) — optional, off by default (Task #35)
    # -------------------------------------------------------------------------
    stripe_metering_enabled: bool = False
    stripe_api_key: Optional[SecretStr] = None
    #: When set, overrides the logical event name sent as Stripe `event_name` (meter name).
    stripe_meter_event_name: Optional[str] = None

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value  # type: ignore[return-value]

    @model_validator(mode="after")
    def validate_production_requirements(self) -> "Settings":
        if self.app_env == "production":
            if not self.openai_api_key and not self.gcp_project_id:
                raise ValueError("Production requires either OPENAI_API_KEY or GCP_PROJECT_ID")
            if self.debug:
                raise ValueError("DEBUG must be False in production")
        return self

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
