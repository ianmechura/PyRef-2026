from __future__ import annotations

from uuid import UUID

from taskflow_ref.application.ports import TaskNotifier, TaskRepository
from taskflow_ref.domain.models import Priority, Task


class TaskNotFoundError(LookupError):
    def __init__(self, task_id: UUID) -> None:
        super().__init__(f"Task not found: {task_id}")
        self.task_id = task_id


class TaskService:
    def __init__(self, repository: TaskRepository, notifier: TaskNotifier | None = None) -> None:
        self._repository = repository
        self._notifier = notifier

    def create_task(self, title: str, priority: Priority = Priority.NORMAL) -> Task:
        task = Task.create(title=title, priority=priority)
        self._repository.save(task)

        if self._notifier is not None:
            self._notifier.task_created(task)

        return task

    def complete_task(self, task_id: UUID) -> Task:
        existing = self._repository.get(task_id)
        if existing is None:
            raise TaskNotFoundError(task_id)

        completed = existing.complete()
        self._repository.save(completed)

        if self._notifier is not None:
            self._notifier.task_completed(completed)

        return completed

    def list_tasks(self) -> list[Task]:
        return sorted(self._repository.list(), key=lambda task: task.created_at)
