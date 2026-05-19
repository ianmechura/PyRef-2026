from __future__ import annotations

import time

import httpx

from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.serialization import TaskRecord


class NoOpTaskNotifier:
    def task_created(self, task: Task) -> None:
        return None

    def task_completed(self, task: Task) -> None:
        return None


class WebhookTaskNotifier:
    def __init__(
        self,
        url: str,
        timeout_seconds: float = 3.0,
        retries: int = 2,
        client: httpx.Client | None = None,
    ) -> None:
        self._url = url
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._client = client or httpx.Client(timeout=timeout_seconds)

    def task_created(self, task: Task) -> None:
        self._post_event("task.created", task)

    def task_completed(self, task: Task) -> None:
        self._post_event("task.completed", task)

    def _post_event(self, event_name: str, task: Task) -> None:
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
