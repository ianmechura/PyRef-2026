"""Notifier adapters implementing the ``TaskNotifier`` port.

Provides a null-object implementation and an HTTP webhook
implementation, both interchangeable behind the application's port.
"""

from __future__ import annotations

import time

import httpx

from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.serialization import TaskRecord


class NoOpTaskNotifier:
    """Null-object notifier that intentionally does nothing.

    Best practices demonstrated:
        - The Null Object pattern: callers invoke notifications
          unconditionally without ``if notifier:`` guards, removing
          branching and making "notifications disabled" a first-class,
          fully-typed configuration.
    """

    def task_created(self, task: Task) -> None:
        """No-op; satisfies the port without side effects."""
        return None

    def task_completed(self, task: Task) -> None:
        """No-op; satisfies the port without side effects."""
        return None


class WebhookTaskNotifier:
    """Posts task events to an HTTP webhook with bounded retries.

    Best practices demonstrated:
        - Network I/O is isolated in an infrastructure adapter, never
          in the domain/application layers.
    """

    def __init__(
        self,
        url: str,
        timeout_seconds: float = 3.0,
        retries: int = 2,
        client: httpx.Client | None = None,
    ) -> None:
        """Configure the webhook target and HTTP client.

        Best practices demonstrated:
            - The ``httpx.Client`` is injectable: production constructs
              a default client, while tests pass a transport-mocked
              client — no global patching needed (seam for testing).
            - Network calls always have an explicit timeout; an
              unbounded request can hang a worker indefinitely.

        Args:
            url: Destination webhook URL.
            timeout_seconds: Per-request timeout.
            retries: Number of additional attempts after the first.
            client: Optional pre-configured client (used in tests).
        """
        self._url = url
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._client = client or httpx.Client(timeout=timeout_seconds)

    def task_created(self, task: Task) -> None:
        """Emit a ``task.created`` event.

        Best practices demonstrated:
            - Thin public method delegating to a shared private helper,
              keeping event-name strings in one place (DRY).
        """
        self._post_event("task.created", task)

    def task_completed(self, task: Task) -> None:
        """Emit a ``task.completed`` event (delegates to the helper)."""
        self._post_event("task.completed", task)

    def _post_event(self, event_name: str, task: Task) -> None:
        """POST an event payload, retrying transient HTTP failures.

        Best practices demonstrated:
            - The payload is built from the ``TaskRecord`` DTO so only
              JSON-safe data crosses the wire, never the raw domain
              object.
            - ``response.raise_for_status()`` converts non-2xx
              responses into exceptions instead of silently treating a
              500 as success.
            - Only the specific ``httpx.HTTPError`` family is caught —
              never a bare ``except`` — so programming errors still
              surface.
            - Retries are bounded (``range(self._retries + 1)``) and the
              final failure is re-raised, with an incremental backoff
              (``0.1 * (attempt + 1)``) to avoid hammering a struggling
              endpoint.

        Args:
            event_name: Event type, e.g. ``"task.created"``.
            task: The task the event concerns.

        Raises:
            httpx.HTTPError: If every attempt fails.
        """
        payload = {
            "event": event_name,
            "task": TaskRecord.from_domain(task).model_dump(mode="json"),
        }

        for attempt in range(self._retries + 1):
            try:
                response = self._client.post(self._url, json=payload)
                response.raise_for_status()
                return
            except httpx.HTTPError:
                if attempt >= self._retries:
                    raise
                time.sleep(0.1 * (attempt + 1))
