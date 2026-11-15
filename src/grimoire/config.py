"""Typed settings loaded from `.env` and the environment.

Other modules call `get_settings()` and never read environment variables
themselves. Real environment variables win over values in `.env`; unknown
variables in `.env` are ignored.
"""

from functools import lru_cache
from typing import Annotated
from urllib.parse import quote

from pydantic import SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class ConfigError(ValueError):
    """Settings are missing or invalid. The message never contains secret values."""


class Settings(BaseSettings):
    """All application settings; field names match the environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    postgres_user: str = "grimoire"
    postgres_password: SecretStr
    postgres_db: str = "grimoire"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432

    # Model server (llama-server, OpenAI-compatible API)
    llama_base_url: str
    llama_api_key: SecretStr
    llama_model: str

    # Telegram (optional here; the bot checks for them when it starts)
    telegram_bot_token: SecretStr | None = None
    telegram_club_chat_id: int | None = None
    telegram_allowed_user_ids: Annotated[list[int], NoDecode] = []

    @field_validator("telegram_bot_token", "telegram_club_chat_id", mode="before")
    @classmethod
    def _empty_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("telegram_allowed_user_ids", mode="before")
    @classmethod
    def _split_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    def database_url(self, scheme: str = "postgresql") -> str:
        """Connection URL with the password quoted.

        Contains the password, so it is a method (not a field) and stays out of
        repr and model dumps. The driver prefix is decided in issue #6; pass
        another `scheme` (e.g. "postgresql+psycopg") to change it.
        """
        password = quote(self.postgres_password.get_secret_value(), safe="")
        user = quote(self.postgres_user, safe="")
        return (
            f"{scheme}://{user}:{password}@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )


def load_settings(env_file: str | None = ".env") -> Settings:
    """Build settings, turning validation errors into a readable ConfigError."""
    try:
        return Settings(_env_file=env_file)
    except ValidationError as exc:
        missing, invalid = [], []
        for err in exc.errors():
            name = str(err["loc"][0]).upper()
            if err["type"] == "missing":
                missing.append(name)
            else:
                invalid.append(f"{name} ({err['msg']})")
        parts = []
        if missing:
            parts.append(f"Missing required settings: {', '.join(missing)}.")
        if invalid:
            parts.append(f"Invalid settings: {'; '.join(invalid)}.")
        parts.append("Set them in .env or the environment; see .env.example.")
        raise ConfigError(" ".join(parts)) from None


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor; created on first call, never at import time."""
    return load_settings()
