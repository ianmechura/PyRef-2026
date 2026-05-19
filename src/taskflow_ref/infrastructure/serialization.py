"""Serialization boundary between the domain and persisted JSON.

A dedicated wire/storage model keeps the domain object free of
serialization concerns. The domain can evolve independently of the
on-disk format, and explicit mappers make schema changes visible.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from taskflow_ref.domain.models import Priority, Task, TaskStatus


class TaskRecord(BaseModel):
    """Pydantic DTO mirroring ``Task`` for storage/transport.

    Best practices demonstrated:
        - Separate persistence model (DTO) from the domain model, so
          serialization rules never leak into domain logic and the two
          can version independently.
        - Pydantic handles validation and JSON-safe (de)serialization
          of ``UUID``/``datetime``/enum types instead of hand-written,
          error-prone conversion code.
    """

    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None = None

    @staticmethod
    def from_domain(task: Task) -> "TaskRecord":
        """Map a domain ``Task`` to its persistence record.

        Best practices demonstrated:
            - An explicit, total field-by-field mapper makes the domain
              → storage boundary auditable; adding a field forces a
              visible change here rather than silently passing through.

        Args:
            task: The domain object to convert.

        Returns:
            A ``TaskRecord`` ready to be serialized.
        """
        return TaskRecord(
            id=task.id,
            title=task.title,
            priority=task.priority,
            status=task.status,
            created_at=task.created_at,
            completed_at=task.completed_at,
        )

    def to_domain(self) -> Task:
        """Reconstruct a domain ``Task`` from this record.

        Best practices demonstrated:
            - Inbound data is funneled back through the typed domain
              constructor, so persisted values are rehydrated into the
              immutable domain object rather than leaking the DTO into
              business code.

        Returns:
            The equivalent domain ``Task``.
        """
        return Task(
            id=self.id,
            title=self.title,
            priority=self.priority,
            status=self.status,
            created_at=self.created_at,
            completed_at=self.completed_at,
        )
