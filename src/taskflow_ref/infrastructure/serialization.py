from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from taskflow_ref.domain.models import Priority, Task, TaskStatus


class TaskRecord(BaseModel):
    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None = None

    @staticmethod
    def from_domain(task: Task) -> "TaskRecord":
        return TaskRecord(
            id=task.id,
            title=task.title,
            priority=task.priority,
            status=task.status,
            created_at=task.created_at,
            completed_at=task.completed_at,
        )

    def to_domain(self) -> Task:
        return Task(
            id=self.id,
            title=self.title,
            priority=self.priority,
            status=self.status,
            created_at=self.created_at,
            completed_at=self.completed_at,
        )
