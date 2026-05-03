from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///./careerfit_dev.db"
    app_name: str = "CareerFit Agent"
    environment: str = "development"

    model_config = SettingsConfigDict(env_prefix="CAREERFIT_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
