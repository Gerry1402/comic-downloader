from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_path: Path = Path.home() / "Comics"
    webtoon: str = ""
    tapas: str = ""
    vortex: str = ""
    flame: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env.path", ".env.cookies"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
