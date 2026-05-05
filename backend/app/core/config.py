from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


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
    llm_concurrent_enabled: bool = True

    model_config = SettingsConfigDict(env_prefix="CAREERFIT_", env_file=str(_PROJECT_ROOT / ".env"), env_file_encoding="utf-8", extra="ignore")

    @field_validator("llm_timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        if v < 30.0:
            raise ValueError("llm_timeout_seconds must be at least 30 seconds")
        if v > 300.0:
            raise ValueError("llm_timeout_seconds must be at most 300 seconds (5 minutes)")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
