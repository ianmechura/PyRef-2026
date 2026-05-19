from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TaskStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class Task:
    id: UUID
    title: str
    priority: Priority
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None = None

    @staticmethod
    def create(title: str, priority: Priority = Priority.NORMAL) -> "Task":
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
