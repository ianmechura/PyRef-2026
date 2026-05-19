from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.file_repository import JsonTaskRepository


def test_repository_round_trips_tasks(tmp_path) -> None:
    repository = JsonTaskRepository(tmp_path / "tasks.json")
    task = Task.create("Persist me")

    repository.save(task)

    assert repository.get(task.id) == task
    assert repository.list() == [task]
