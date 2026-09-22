"""System Configuration Management for FinGuard-AI.

Enforces 12-Factor App design principles via type-safe environment variables.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable application settings container."""

    # Service Identification
    PROJECT_NAME: str = "FinGuard-AI Compliance & Regulatory Audit Pipeline"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Networking & Gateways
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DASHBOARD_PORT: int = 8501
    CORS_ORIGINS: List[str] = ["*"]

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Provides a thread-safe cached singleton settings instance."""
    return Settings()