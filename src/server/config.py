from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SERVER_ROOT = os.path.dirname(__file__)


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

    # Wallet providers
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    PLAID_REDIRECT_URI: str = ""
    PLAID_TOKEN_ENCRYPTION_KEY: str = ""
    GOLDRUSH_API_KEY: str = ""
    SYNC_JOB_TIMEOUT_SECONDS: int = 300
    SYNC_MAX_RETRIES: int = 3

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ORIGIN_REGEX: str = r"https?://(localhost|127\.0\.0\.1)(:\d+)?$|https://.*\.github\.dev$|https://.*\.app\.github\.dev$"

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(PROJECT_ROOT, ".env"),
            os.path.join(SERVER_ROOT, ".env"),
        ),
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
