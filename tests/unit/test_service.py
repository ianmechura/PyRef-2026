from uuid import UUID

import pytest

from taskflow_ref.application.service import TaskNotFoundError, TaskService
from taskflow_ref.domain.models import Task


class InMemoryRepository:
    def __init__(self) -> None:
        self.tasks: dict[UUID, Task] = {}

    def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get(self, task_id: UUID) -> Task | None:
        return self.tasks.get(task_id)

    def list(self) -> list[Task]:
        return list(self.tasks.values())


class SpyNotifier:
    def __init__(self) -> None:
        self.events: list[str] = []

    def task_created(self, task: Task) -> None:
        self.events.append(f"created:{task.id}")

    def task_completed(self, task: Task) -> None:
        self.events.append(f"completed:{task.id}")


def test_service_creates_and_notifies() -> None:
    repository = InMemoryRepository()
    notifier = SpyNotifier()
    service = TaskService(repository=repository, notifier=notifier)

    task = service.create_task("Write tests")

    assert repository.get(task.id) == task
    assert notifier.events == [f"created:{task.id}"]


def test_complete_unknown_task_raises() -> None:
    service = TaskService(repository=InMemoryRepository())

    with pytest.raises(TaskNotFoundError):
        service.complete_task(UUID("00000000-0000-0000-0000-000000000000"))
