from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class HASettings(BaseSettings):
    url: str = "http://homeassistant.local:8123"
    token: str = ""
    verify_ssl: bool = True

    model_config = {"env_prefix": "HA_"}


class Settings(BaseSettings):
    ha: HASettings = Field(default_factory=HASettings)
    log_level: str = "INFO"

    model_config = {"env_nested_delimiter": "__"}


def get_settings() -> Settings:
    return Settings()
