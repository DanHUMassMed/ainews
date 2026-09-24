from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Industry News Daily"
    API_V1_STR: str = "/api"
    
    # Network & Host Binding
    APP_HOST: str = "192.168.1.101"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173
    
    # Database
    POSTGRES_USER: str = "ainews"
    POSTGRES_PASSWORD: str = "ainews_secret"
    POSTGRES_DB: str = "ainews"
    DATABASE_URL: str = "postgresql+asyncpg://ainews:ainews_secret@127.0.0.1:5432/ainews"
    SYNC_DATABASE_URL: str = "postgresql://ainews:ainews_secret@127.0.0.1:5432/ainews"
    
    # External Services
    SEARXNG_URL: str = "http://127.0.0.1:8080"
    FIRECRAWL_URL: str = "http://127.0.0.1:3002"
    
    # Security
    EDITORIAL_SECRET_KEY: str = "hermes_editorial_secret_token_change_in_production"
    ADMIN_API_TOKEN: str = "admin_editorial_secret_token_change_in_production"
    EDITORIAL_ADMIN_PASSWORD: str = "P@ssw0rd"
    
    # Editorial Defaults
    DISCOVERY_LOOKBACK_HOURS: int = 28
    EDITORIAL_LOOKBACK_DAYS: int = 28
    FEEDBACK_COLD_START_DAYS: int = 30
    FEEDBACK_COLD_START_THRESHOLD: int = 100
    MIN_STORIES_PER_EDITION: int = 5
    TARGET_STORIES_PER_EDITION: int = 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
