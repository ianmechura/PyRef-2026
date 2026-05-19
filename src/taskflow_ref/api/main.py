from __future__ import annotations

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status

from taskflow_ref.api.schemas import CreateTaskRequest, TaskResponse
from taskflow_ref.application.service import TaskNotFoundError, TaskService
from taskflow_ref.composition import build_task_service
from taskflow_ref.infrastructure.settings import Settings
from taskflow_ref.observability.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    resolved_settings = settings or Settings.from_env()
    service = build_task_service(resolved_settings)

    app = FastAPI(title="TaskFlow Reference API", version="0.1.0")

    def get_service() -> TaskService:
        return service

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create_task(
        request: CreateTaskRequest,
        task_service: TaskService = Depends(get_service),
    ) -> TaskResponse:
        task = task_service.create_task(title=request.title, priority=request.priority)
        return TaskResponse.from_domain(task)

    @app.get("/tasks", response_model=list[TaskResponse])
    def list_tasks(task_service: TaskService = Depends(get_service)) -> list[TaskResponse]:
        return [TaskResponse.from_domain(task) for task in task_service.list_tasks()]

    @app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
    def complete_task(
        task_id: UUID,
        task_service: TaskService = Depends(get_service),
    ) -> TaskResponse:
        try:
            task = task_service.complete_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return TaskResponse.from_domain(task)

    return app
