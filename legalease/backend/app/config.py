"""Application configuration.

All secrets and environment-specific values are read from the environment.
Never hardcode an API key or a model name here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime settings sourced from ``backend/.env`` and the process env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -------------------------------------------------
    app_name: str = "LegalEase API"
    app_version: str = "1.0.0"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False

    # --- Database ----------------------------------------------------
    # SQLite for local development. Swap for a PostgreSQL DSN in production,
    # e.g. postgresql+psycopg://user:pass@localhost:5432/legalease
    database_url: str = Field(
        default=f"sqlite:///{(BACKEND_DIR / 'legalease.db').as_posix()}"
    )

    # --- AI ----------------------------------------------------------
    # Both values are optional. The app boots and serves every read-only
    # endpoint without them, and reports `unconfigured` rather than crashing.
    groq_api_key: str | None = None
    # Resolved from GROQ_MODEL. Never baked into the source, so switching or
    # retiring a model is an environment change rather than a code change.
    groq_model: str = "openai/gpt-oss-120b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_timeout_seconds: float = 120.0
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.3
    # One extra attempt with a larger token budget when a reply is cut short.
    groq_max_retries: int = 2

    # Deterministic offline output when no API key is available.
    demo_mode: bool = False

    # --- Frontend / CORS ---------------------------------------------
    frontend_url: str = "http://localhost:5173"

    # --- Uploads -----------------------------------------------------
    upload_dir: Path = BACKEND_DIR / "uploads"
    max_logo_bytes: int = 2 * 1024 * 1024  # 2 MB
    allowed_logo_content_types: tuple[str, ...] = (
        "image/png",
        "image/jpeg",
    )

    # --- Request limits ----------------------------------------------
    max_parties: int = 20
    max_clauses: int = 60
    max_instructions_chars: int = 4000
    max_free_text_chars: int = 2000

    @field_validator("frontend_url")
    @classmethod
    def _normalize_frontend_url(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("groq_base_url")
    @classmethod
    def _normalize_groq_base_url(cls, value: str) -> str:
        return value.rstrip("/")

    @property
    def logo_dir(self) -> Path:
        return self.upload_dir / "logos"

    @property
    def allowed_origins(self) -> list[str]:
        """Explicit allowlist. Never returns ``*``."""
        origins = [self.frontend_url]
        if self.environment != "production":
            # 127.0.0.1 is a distinct origin from localhost.
            for candidate in ("http://127.0.0.1:5173", "http://localhost:5173"):
                if candidate not in origins:
                    origins.append(candidate)
        return origins

    @property
    def ai_configured(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.strip())

    @property
    def ai_mode(self) -> Literal["groq", "demo", "unconfigured"]:
        if self.ai_configured:
            return "groq"
        if self.demo_mode:
            return "demo"
        return "unconfigured"

    def ensure_directories(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.logo_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
