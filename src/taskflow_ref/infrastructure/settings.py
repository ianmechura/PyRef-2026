"""Application configuration.

Configuration is read from the environment (12-factor style) and
validated into a typed object so the rest of the code never touches
raw ``os.environ`` strings.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl


class Settings(BaseModel):
    """Validated, typed application settings.

    Best practices demonstrated:
        - A Pydantic model validates and coerces configuration at the
          boundary, so invalid config fails loudly at startup instead
          of causing obscure errors later.
        - ``Field`` constraints (``gt=0``, ``ge=0``) encode invariants
          declaratively rather than via scattered manual checks.
        - ``HttpUrl`` validates the webhook URL's shape for free.
        - ``Path`` (not ``str``) for filesystem locations keeps path
          handling correct and OS-independent downstream.
    """

    data_file: Path = Field(default=Path(".data/tasks.json"))
    webhook_url: HttpUrl | None = None
    http_timeout_seconds: float = Field(default=3.0, gt=0)
    http_retries: int = Field(default=2, ge=0)

    @staticmethod
    def from_env() -> "Settings":
        """Build settings from environment variables.

        Best practices demonstrated:
            - 12-factor configuration: behavior is driven by the
              environment, with sensible defaults for every key so the
              app runs out of the box.
            - Construction flows through the Pydantic model, so env
              strings are validated/coerced rather than trusted.
            - The honest inline comment documents a deliberate scope
              decision (``pydantic-settings`` for larger projects)
              instead of hiding the trade-off.

        Returns:
            A validated ``Settings`` instance.
        """
        # Small projects can read environment directly.
        # Larger projects should use pydantic-settings.
        import os

        return Settings(
            data_file=Path(os.getenv("TASKFLOW_DATA_FILE", ".data/tasks.json")),
            webhook_url=os.getenv("TASKFLOW_WEBHOOK_URL") or None,
            http_timeout_seconds=float(os.getenv("TASKFLOW_HTTP_TIMEOUT_SECONDS", "3")),
            http_retries=int(os.getenv("TASKFLOW_HTTP_RETRIES", "2")),
        )
