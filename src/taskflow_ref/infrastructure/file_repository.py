from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.serialization import TaskRecord


class JsonTaskRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, task: Task) -> None:
        tasks = {item.id: item for item in self.list()}
        tasks[task.id] = task
        self._write_all(list(tasks.values()))

    def get(self, task_id: UUID) -> Task | None:
        return next((task for task in self.list() if task.id == task_id), None)

    def list(self) -> list[Task]:
        if not self._path.exists():
            return []

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"Expected list in task repository file: {self._path}")

        return [TaskRecord.model_validate(item).to_domain() for item in raw]

    def _write_all(self, tasks: list[Task]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        records = [TaskRecord.from_domain(task).model_dump(mode="json") for task in tasks]
        self._path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
