"""Application settings."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agentic-sales-assistant"
    app_env: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    hubspot_access_token: str | None = None
    hubspot_base_url: str = "https://api.hubapi.com"
    enable_crm_simulation: bool = True

    db_url: str = "sqlite:///./sales_assistant.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
