from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Единая конфигурация приложения.

    Все настройки берём из переменных окружения или .env.
    Так проще менять dev/stage/prod без изменения кода.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Edu Whiteboard API"
    app_env: str = "local"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://edu:edu@localhost:5432/edu_whiteboard"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    log_level: str = "INFO"

    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"

    db_pool_size: int = Field(default=10, ge=1)
    db_max_overflow: int = Field(default=20, ge=0)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # Кэшируем настройки, чтобы не читать .env на каждый запрос.
    return Settings()
