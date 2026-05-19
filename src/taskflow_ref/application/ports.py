"""Application ports (the "P" in ports-and-adapters).

These ``Protocol`` classes define the interfaces the application layer
depends on. Concrete adapters live in ``infrastructure`` and are wired
in at composition time, so the application never imports infrastructure
directly — the dependency arrow points inward.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from taskflow_ref.domain.models import Task


class TaskRepository(Protocol):
    """Persistence port for tasks.

    Best practices demonstrated:
        - ``typing.Protocol`` enables structural typing: adapters
          conform by shape, with no inheritance or registration. This
          is the Dependency Inversion Principle — the application owns
          the interface, infrastructure implements it.
        - The abstraction hides the storage mechanism (JSON file, SQL,
          in-memory fake) so tests can substitute a trivial fake.
    """

    def save(self, task: Task) -> None:
        """Insert or replace a task by id."""
        ...

    def get(self, task_id: UUID) -> Task | None:
        """Return the task with ``task_id``, or ``None`` if absent.

        Returning ``None`` rather than raising lets the caller decide
        how a missing task should be handled.
        """
        ...

    def list(self) -> list[Task]:
        """Return all stored tasks."""
        ...


class TaskNotifier(Protocol):
    """Outbound notification port for task lifecycle events.

    Best practices demonstrated:
        - Side effects (webhooks, emails) sit behind a port so the
          domain/application stays pure and a no-op implementation can
          be injected in tests or when notifications are disabled.
    """

    def task_created(self, task: Task) -> None:
        """Notify subscribers that a task was created."""
        ...

    def task_completed(self, task: Task) -> None:
        """Notify subscribers that a task was completed."""
        ...
