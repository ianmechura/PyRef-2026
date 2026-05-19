"""Application services: use-case orchestration.

This layer coordinates the domain and the ports. It contains no
business rules of its own (those live in the domain) and no I/O details
(those live in infrastructure) — it just sequences the steps of each
use case.
"""

from __future__ import annotations

from uuid import UUID

from taskflow_ref.application.ports import TaskNotifier, TaskRepository
from taskflow_ref.domain.models import Priority, Task


class TaskNotFoundError(LookupError):
    """Raised when a task id does not resolve to a stored task.

    Best practices demonstrated:
        - A specific, domain-named exception subclassing the relevant
          builtin (``LookupError``) lets callers catch this precise
          failure without over-broad ``except`` clauses.
        - The offending ``task_id`` is attached as an attribute so
          handlers can react programmatically, not just log a string.
    """

    def __init__(self, task_id: UUID) -> None:
        """Build the error with a human-readable message and the id.

        Calling ``super().__init__`` keeps standard exception behavior
        (``str(exc)``, traceback rendering) intact.
        """
        super().__init__(f"Task not found: {task_id}")
        self.task_id = task_id


class TaskService:
    """Coordinates task use cases over the repository and notifier ports.

    Best practices demonstrated:
        - Constructor dependency injection: collaborators are passed in
          and typed against the ``Protocol`` ports, never constructed
          internally. This keeps the service testable and decoupled
          from concrete infrastructure.
    """

    def __init__(self, repository: TaskRepository, notifier: TaskNotifier | None = None) -> None:
        """Store injected collaborators.

        Best practices demonstrated:
            - Depend on abstractions (the port protocols), not concrete
              classes.
            - ``notifier`` is optional (``| None``) so notifications can
              be cleanly disabled without a null-object requirement at
              the call site.
        """
        self._repository = repository
        self._notifier = notifier

    def create_task(self, title: str, priority: Priority = Priority.NORMAL) -> Task:
        """Create, persist, and announce a new task.

        Best practices demonstrated:
            - The service orchestrates but delegates: validation lives
              in ``Task.create``, persistence in the repository,
              announcement in the notifier — single responsibility per
              collaborator.
            - The optional notifier is guarded with an explicit
              ``is not None`` check rather than truthiness.

        Args:
            title: Title for the new task.
            priority: Priority, defaulting to ``Priority.NORMAL``.

        Returns:
            The newly created, persisted ``Task``.
        """
        task = Task.create(title=title, priority=priority)
        self._repository.save(task)

        if self._notifier is not None:
            self._notifier.task_created(task)

        return task

    def complete_task(self, task_id: UUID) -> Task:
        """Mark an existing task completed and persist the change.

        Best practices demonstrated:
            - Fail fast with a domain-specific error when the task is
              missing, instead of returning ``None`` and pushing the
              problem downstream.
            - The state transition is delegated to the immutable domain
              method ``Task.complete``; the service only persists and
              announces the result.

        Args:
            task_id: Identifier of the task to complete.

        Returns:
            The completed ``Task``.

        Raises:
            TaskNotFoundError: If no task with ``task_id`` exists.
        """
        existing = self._repository.get(task_id)
        if existing is None:
            raise TaskNotFoundError(task_id)

        completed = existing.complete()
        self._repository.save(completed)

        if self._notifier is not None:
            self._notifier.task_completed(completed)

        return completed

    def list_tasks(self) -> list[Task]:
        """Return all tasks ordered by creation time.

        Best practices demonstrated:
            - Sorting is an application concern applied here rather than
              relying on incidental storage order, so the result is
              deterministic regardless of the repository adapter.
            - A ``key`` function (not ``cmp``) is used for the sort, the
              idiomatic and efficient Python approach.

        Returns:
            Tasks sorted ascending by ``created_at``.
        """
        return sorted(self._repository.list(), key=lambda task: task.created_at)
