from __future__ import annotations

from typing import Protocol
from uuid import UUID

from taskflow_ref.domain.models import Task


class TaskRepository(Protocol):
    def save(self, task: Task) -> None: ...

    def get(self, task_id: UUID) -> Task | None: ...

    def list(self) -> list[Task]: ...


class TaskNotifier(Protocol):
    def task_created(self, task: Task) -> None: ...

    def task_completed(self, task: Task) -> None: ...
