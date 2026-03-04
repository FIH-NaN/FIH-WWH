from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""

    # API
    API_TITLE: str = "Wealth Wellness Hub API"
    API_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./wealth_hub.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # External services (optional for local dev)
    OPENAI_API_KEY: Optional[str] = None
    WEB3_RPC_URL: Optional[str] = None

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins from comma-separated env value."""
        value = (self.CORS_ORIGINS or "").strip()
        if not value:
            return []
        if value.startswith("[") and value.endswith("]"):
            # Support JSON-array style env value as fallback.
            import json

            parsed = json.loads(value)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
