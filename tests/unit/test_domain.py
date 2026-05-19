from taskflow_ref.domain.models import Priority, Task, TaskStatus


def test_create_task_trims_title_and_defaults_open() -> None:
    task = Task.create("  Probe board  ", priority=Priority.HIGH)

    assert task.title == "Probe board"
    assert task.priority == Priority.HIGH
    assert task.status == TaskStatus.OPEN


def test_complete_task_returns_completed_copy() -> None:
    task = Task.create("Run job")
    completed = task.complete()

    assert task.status == TaskStatus.OPEN
    assert completed.status == TaskStatus.COMPLETED
    assert completed.completed_at is not None
