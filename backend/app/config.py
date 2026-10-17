"""Validated local connection settings. Password values never enter health output."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FALKORDB_", extra="ignore", frozen=True, hide_input_in_errors=True
    )

    host: str = Field(default="127.0.0.1", min_length=1)
    port: int = Field(default=6379, ge=1, le=65535)
    browser_port: int = Field(default=3000, ge=1, le=65535)
    graph: str = Field(default="civicly_knowledge", pattern=r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
    username: str | None = None
    password: SecretStr | None = None
    connect_timeout_seconds: float = Field(default=2, gt=0, le=30)
    socket_timeout_seconds: float = Field(default=3, gt=0, le=30)
    query_timeout_ms: int = Field(default=1000, gt=0, le=10000)
