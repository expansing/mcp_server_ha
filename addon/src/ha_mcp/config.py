from __future__ import annotations

from pydantic_settings import BaseSettings


class HASettings(BaseSettings):
    url: str = "http://homeassistant.local:8123"
    token: str = ""
    verify_ssl: bool = True


class Settings(BaseSettings):
    ha: HASettings = HASettings()
    log_level: str = "INFO"

    model_config = {"env_nested_delimiter": "__"}


def get_settings() -> Settings:
    return Settings()
