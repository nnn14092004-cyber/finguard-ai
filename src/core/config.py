"""System Configuration Management for FinGuard.

Enforces 12-Factor App design principles via type-safe environment variables.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable application settings container."""

    # Service Identification
    PROJECT_NAME: str = "FinGuard Compliance & Regulatory Audit Pipeline"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Networking & Gateways
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DASHBOARD_PORT: int = 8501
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit

    # Regulatory Scoring Thresholds
    TIER1_CRITICAL_PENALTY: int = 40
    TIER2_HIGH_PENALTY: int = 20
    TIER3_CAUTION_PENALTY: int = 10
    RED_FLAG_THRESHOLD: int = 75
    ORANGE_FLAG_THRESHOLD: int = 50
    YELLOW_FLAG_THRESHOLD: int = 25

    # Storage & Audit Telemetry
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    AUDIT_LOG_RETENTION_DAYS: int = 90
    ENABLE_STRUCTURED_JSON_LOGGING: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parses comma-separated strings into a validated origin list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:8501"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Provides a thread-safe cached singleton settings instance."""
    return Settings()
