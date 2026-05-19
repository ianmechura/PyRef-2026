from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl


class Settings(BaseModel):
    data_file: Path = Field(default=Path(".data/tasks.json"))
    webhook_url: HttpUrl | None = None
    http_timeout_seconds: float = Field(default=3.0, gt=0)
    http_retries: int = Field(default=2, ge=0)

    @staticmethod
    def from_env() -> "Settings":
        # Small projects can read environment directly.
        # Larger projects should use pydantic-settings.
        import os

        return Settings(
            data_file=Path(os.getenv("TASKFLOW_DATA_FILE", ".data/tasks.json")),
            webhook_url=os.getenv("TASKFLOW_WEBHOOK_URL") or None,
            http_timeout_seconds=float(os.getenv("TASKFLOW_HTTP_TIMEOUT_SECONDS", "3")),
            http_retries=int(os.getenv("TASKFLOW_HTTP_RETRIES", "2")),
        )
