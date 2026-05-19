from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from taskflow_ref.domain.models import Priority, Task, TaskStatus


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    priority: Priority = Priority.NORMAL


class TaskResponse(BaseModel):
    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None

    @staticmethod
    def from_domain(task: Task) -> "TaskResponse":
        return TaskResponse(
            id=task.id,
            title=task.title,
            priority=task.priority,
            status=task.status,
            created_at=task.created_at,
            completed_at=task.completed_at,
        )
