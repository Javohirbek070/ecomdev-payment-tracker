import os
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./learning_center.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    environment: str = "development"
    api_base_url: str = "http://127.0.0.1:8000"

    # Telegram bot configuration
    telegram_bot_token: str | None = None
    telegram_admin_ids: list[int] | str = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="after")
    @classmethod
    def adjust_for_vercel(cls, v: str) -> str:
        # On Vercel serverless functions, the root filesystem is read-only.
        # Use /tmp for SQLite persistent storage across function invocations.
        if os.getenv("VERCEL") and "learning_center.db" in v and not v.startswith("sqlite:////tmp/"):
            return "sqlite:////tmp/learning_center.db"
        return v

    @field_validator("telegram_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> list[int]:
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            ids: list[int] = []
            for item in v.split(","):
                item = item.strip()
                if item:
                    try:
                        ids.append(int(item))
                    except ValueError:
                        pass
            return ids
        if isinstance(v, (list, tuple, set)):
            return [int(x) for x in v if str(x).strip().isdigit() or isinstance(x, int)]
        return []


settings = Settings()

