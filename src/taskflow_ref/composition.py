"""Composition root.

This is the single place where concrete infrastructure classes are
instantiated and wired into the application. Centralizing object graph
construction here keeps every other module dependency-direction-clean
and free of ``import``-time wiring.
"""

from __future__ import annotations

from taskflow_ref.application.service import TaskService
from taskflow_ref.infrastructure.file_repository import JsonTaskRepository
from taskflow_ref.infrastructure.notifier import NoOpTaskNotifier, WebhookTaskNotifier
from taskflow_ref.infrastructure.settings import Settings


def build_task_service(settings: Settings) -> TaskService:
    """Assemble a ``TaskService`` with concrete adapters from settings.

    Best practices demonstrated:
        - Composition-root pattern: this function is the only place
          that knows about concrete adapter classes, so the rest of
          the codebase depends solely on ports/abstractions.
        - Configuration-driven wiring: the notifier adapter is selected
          from settings (webhook when a URL is configured, otherwise
          the no-op null object), so behavior changes via config, not
          code edits.
        - Manual dependency injection — explicit and framework-free —
          keeps the wiring obvious and easy to follow in tests.

    Args:
        settings: Validated application settings driving adapter
            selection and configuration.

    Returns:
        A fully wired ``TaskService`` ready for use by any entry point.
    """
    repository = JsonTaskRepository(settings.data_file)

    notifier = (
        WebhookTaskNotifier(
            url=str(settings.webhook_url),
            timeout_seconds=settings.http_timeout_seconds,
            retries=settings.http_retries,
        )
        if settings.webhook_url is not None
        else NoOpTaskNotifier()
    )

    return TaskService(repository=repository, notifier=notifier)
