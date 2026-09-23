"""System configuration management for FinGuard.

Enforces 12-Factor App design principles via type-safe environment variables.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import Field, SecretStr, field_validator
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
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DASHBOARD_PORT: int = 8501
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit

    # CORS Origins (Defensively guarded against premature json.loads failure)
    if TYPE_CHECKING:
        CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    else:
        CORS_ORIGINS: Any = Field(
            default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"]
        )

    # Statutory Scoring Thresholds
    TIER1_CRITICAL_PENALTY: int = 40
    TIER2_HIGH_PENALTY: int = 20
    TIER3_CAUTION_PENALTY: int = 10
    RED_FLAG_THRESHOLD: int = 75
    ORANGE_FLAG_THRESHOLD: int = 50
    YELLOW_FLAG_THRESHOLD: int = 25

    # Cognitive LLM Credentials & Telemetry
    GEMINI_API_KEY: SecretStr | str = ""
    LLM_MODEL_NAME: str = "gemini-1.5-flash"
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
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Parses comma-separated strings, JSON arrays, or wildcard tokens into origin list."""
        if v is None:
            return ["http://localhost:3000", "http://localhost:8501"]
        if isinstance(v, str):
            clean_str = v.strip()
            if not clean_str or clean_str in ("*", '""', "''"):
                return ["*"]
            if clean_str.startswith("[") and clean_str.endswith("]"):
                try:
                    parsed = json.loads(clean_str)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [item.strip() for item in clean_str.split(",") if item.strip()]
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if str(item).strip()]
        return ["http://localhost:3000", "http://localhost:8501"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Provides a thread-safe cached singleton settings instance."""
    return Settings()
