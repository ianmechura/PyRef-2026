"""HTTP request/response schemas.

API-facing models are kept separate from the domain model so the
public contract can evolve independently and the domain is never
exposed directly over the wire.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from taskflow_ref.domain.models import Priority, Task, TaskStatus


class CreateTaskRequest(BaseModel):
    """Validated request body for creating a task.

    Best practices demonstrated:
        - Input validation lives at the API edge: ``Field(min_length=1,
          max_length=200)`` rejects bad payloads with an automatic 422
          before any domain code runs.
        - A distinct request model (not the domain object) prevents
          mass-assignment and over-posting of internal fields.
    """

    title: str = Field(min_length=1, max_length=200)
    priority: Priority = Priority.NORMAL


class TaskResponse(BaseModel):
    """Serialized representation of a task returned to clients.

    Best practices demonstrated:
        - A dedicated response model defines an explicit, stable output
          contract instead of leaking the domain object's shape.
    """

    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None

    @staticmethod
    def from_domain(task: Task) -> "TaskResponse":
        """Build the response DTO from a domain ``Task``.

        Best practices demonstrated:
            - An explicit mapper at the boundary decouples the public
              API schema from the internal model, so refactoring the
              domain cannot accidentally change the API contract.

        Args:
            task: The domain task to expose.

        Returns:
            The client-facing ``TaskResponse``.
        """
        return TaskResponse(
            id=task.id,
            title=task.title,
            priority=task.priority,
            status=task.status,
            created_at=task.created_at,
            completed_at=task.completed_at,
        )
