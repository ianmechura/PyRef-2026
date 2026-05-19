from __future__ import annotations

from taskflow_ref.application.service import TaskService
from taskflow_ref.infrastructure.file_repository import JsonTaskRepository
from taskflow_ref.infrastructure.notifier import NoOpTaskNotifier, WebhookTaskNotifier
from taskflow_ref.infrastructure.settings import Settings


def build_task_service(settings: Settings) -> TaskService:
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
