from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///./careerfit_dev.db"
    app_name: str = "CareerFit Agent"
    environment: str = "development"
    llm_enabled: bool = False
    llm_provider: str = "openai_compatible"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_api_style: str = "chat_completions"
    llm_timeout_seconds: float = 20.0

    model_config = SettingsConfigDict(env_prefix="CAREERFIT_", env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
