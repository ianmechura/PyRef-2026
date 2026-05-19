"""JSON-file adapter implementing the ``TaskRepository`` port.

This is an "adapter" in ports-and-adapters terms: it satisfies the
application's repository protocol structurally without importing or
being imported by the application layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from taskflow_ref.domain.models import Task
from taskflow_ref.infrastructure.serialization import TaskRecord


class JsonTaskRepository:
    """File-backed task store satisfying the ``TaskRepository`` port.

    Best practices demonstrated:
        - Structural conformance: no base class is inherited; matching
          the protocol's shape is enough (duck typing made explicit by
          the port).
    """

    def __init__(self, path: Path) -> None:
        """Store the data-file path.

        Best practices demonstrated:
            - Accepts a ``Path`` dependency rather than hard-coding a
              location, so storage placement is configurable/testable.
        """
        self._path = path

    def save(self, task: Task) -> None:
        """Insert or replace a task, then rewrite the store.

        Best practices demonstrated:
            - Upsert semantics expressed via a dict keyed by id, making
              "replace if present" clear and O(n) rather than via
              manual index search and branching.

        Args:
            task: The task to persist (overwrites any task with the
                same id).
        """
        tasks = {item.id: item for item in self.list()}
        tasks[task.id] = task
        self._write_all(list(tasks.values()))

    def get(self, task_id: UUID) -> Task | None:
        """Return the task with ``task_id`` or ``None``.

        Best practices demonstrated:
            - ``next(generator, None)`` finds the first match lazily and
              supplies a default, avoiding ``IndexError`` and the need
              to materialize a filtered list.

        Args:
            task_id: Identifier to look up.

        Returns:
            The matching ``Task``, or ``None`` if not found.
        """
        return next((task for task in self.list() if task.id == task_id), None)

    def list(self) -> list[Task]:
        """Load and return all tasks from disk.

        Best practices demonstrated:
            - Missing file is treated as an empty store (graceful
              first-run behavior) instead of raising.
            - Explicit ``encoding="utf-8"`` makes file I/O deterministic
              across platforms rather than relying on the locale.
            - The decoded shape is validated (``isinstance(raw, list)``)
              and a clear ``ValueError`` with context is raised on
              corruption, instead of failing obscurely later.
            - Each record is validated through ``TaskRecord`` before
              being converted to a domain object.

        Returns:
            All persisted tasks (empty list if the file is absent).

        Raises:
            ValueError: If the file's top-level JSON is not a list.
        """
        if not self._path.exists():
            return []

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"Expected list in task repository file: {self._path}")

        return [TaskRecord.model_validate(item).to_domain() for item in raw]

    def _write_all(self, tasks: list[Task]) -> None:
        """Serialize and atomically-ish replace the store file.

        Best practices demonstrated:
            - Leading underscore marks this as a private helper, keeping
              the public surface limited to the port's methods.
            - Parent directories are created with ``parents=True,
              exist_ok=True`` so first write succeeds and re-writes are
              idempotent.
            - Domain objects are routed through the ``TaskRecord`` DTO's
              ``model_dump(mode="json")`` so only JSON-safe primitives
              are written; ``indent=2`` plus a trailing newline keeps
              the file diff-friendly.

        Args:
            tasks: The full set of tasks to write (full-rewrite store).
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        records = [TaskRecord.from_domain(task).model_dump(mode="json") for task in tasks]
        self._path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
