"""Application configuration via environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All sensitive values are read from the environment or a ``.env`` file.
    Nothing is hardcoded.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://laapp:changeme@localhost:5432/laapp"

    # Application
    APP_NAME: str = "la-app-backend"
    DEBUG: bool = False

    # Local file storage root (relative paths resolve from the backend/ dir)
    STORAGE_ROOT: str = "../storage"


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


settings = get_settings()
