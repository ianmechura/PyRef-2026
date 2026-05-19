"""Structured logging setup.

Logs are emitted as JSON so they are machine-parseable by log
aggregators (ELK, Loki, CloudWatch) instead of relying on brittle
regex parsing of free-form text.
"""

from __future__ import annotations

import json
import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON.

    Best practices demonstrated:
        - Extends the standard ``logging`` framework with a custom
          formatter rather than replacing logging or printing, so
          third-party library logs are captured uniformly.
        - ``record.getMessage()`` is used so ``%``-style lazy log
          arguments are interpolated correctly and only when emitted.
        - Exception info is included only when present, and rendered
          via the framework's ``formatException`` for full tracebacks.
        - ``sort_keys=True`` yields stable key ordering, making log
          output deterministic and diff/test-friendly.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Serialize one ``LogRecord`` to a JSON string.

        Args:
            record: The log record supplied by the logging framework.

        Returns:
            A JSON document containing level, logger, message, and an
            optional formatted exception.
        """
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, sort_keys=True)


def configure_logging(level: int = logging.INFO) -> None:
    """Install the JSON formatter on the root logger.

    Best practices demonstrated:
        - Logging is configured explicitly at application entry points
          (API/CLI), never as an import-time side effect of a library
          module.
        - Existing handlers are cleared first, making the call
          idempotent and avoiding duplicated log lines when invoked
          more than once (e.g. across tests).
        - The log level is a parameter with a sensible default, so it
          can be tuned by callers without code changes.

    Args:
        level: Minimum level for the root logger (default ``INFO``).
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
