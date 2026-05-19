"""Domain model for tasks.

This module is the pure-domain core of the application: no I/O, no
framework imports, no dependency on outer layers. Keeping the domain
free of infrastructure concerns is the central idea of hexagonal
(ports-and-adapters) architecture and makes the business rules trivial
to unit-test.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Priority(StrEnum):
    """Task priority levels.

    Best practices demonstrated:
        - ``StrEnum`` (Python 3.11+) gives a closed set of valid values
          that also serialize as plain strings, replacing error-prone
          "magic string" literals scattered through the codebase.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TaskStatus(StrEnum):
    """Lifecycle state of a task.

    Best practices demonstrated:
        - Modeling a state machine as an enum makes invalid states
          unrepresentable and keeps comparisons type-checked.
    """

    OPEN = "open"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class Task:
    """An immutable task aggregate.

    Best practices demonstrated:
        - ``frozen=True`` makes instances immutable, so state changes
          happen by producing new objects instead of mutating shared
          ones, eliminating a whole class of aliasing bugs.
        - ``slots=True`` removes the per-instance ``__dict__``, lowering
          memory use and preventing accidental attribute typos.
        - Full type annotations on every field enable static checking
          and act as living documentation.
        - ``completed_at: datetime | None`` makes the optional field
          explicit in the type itself.
    """

    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None = None

    @staticmethod
    def create(title: str, priority: Priority = Priority.NORMAL) -> "Task":
        """Construct a valid, OPEN task from raw input.

        Best practices demonstrated:
            - A named factory centralizes construction invariants
              (non-empty title, server-generated id, UTC timestamp,
              initial status) instead of trusting callers to populate
              fields correctly.
            - Input is validated and normalized at the boundary
              (``strip()`` plus an explicit emptiness check), raising a
              precise ``ValueError`` rather than letting an invalid
              object come into existence.
            - ``uuid4()`` generates a collision-resistant identifier
              rather than trusting caller-supplied ids.
            - ``datetime.now(UTC)`` yields a timezone-aware UTC instant;
              naive ``datetime.now()`` is deliberately avoided.

        Args:
            title: Human-readable title; surrounding whitespace is
                stripped and the result must be non-empty.
            priority: Task priority, defaulting to ``Priority.NORMAL``.

        Returns:
            A new ``Task`` in the ``OPEN`` state.

        Raises:
            ValueError: If ``title`` is empty after stripping whitespace.
        """
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")

        return Task(
            id=uuid4(),
            title=clean_title,
            priority=priority,
            status=TaskStatus.OPEN,
            created_at=datetime.now(UTC),
        )

    def complete(self, completed_at: datetime | None = None) -> "Task":
        """Return a completed copy of this task.

        Best practices demonstrated:
            - Immutable state transition: rather than mutating ``self``,
              a new ``Task`` is returned, keeping the original intact.
            - Idempotency: completing an already-completed task returns
              ``self`` unchanged, so repeated calls are safe.
            - The injectable ``completed_at`` parameter allows tests to
              supply a deterministic timestamp instead of patching the
              clock, while production defaults to ``datetime.now(UTC)``.

        Args:
            completed_at: Optional completion instant; defaults to the
                current UTC time when omitted.

        Returns:
            A ``COMPLETED`` ``Task``, or ``self`` if already completed.
        """
        if self.status == TaskStatus.COMPLETED:
            return self

        return Task(
            id=self.id,
            title=self.title,
            priority=self.priority,
            status=TaskStatus.COMPLETED,
            created_at=self.created_at,
            completed_at=completed_at or datetime.now(UTC),
        )
