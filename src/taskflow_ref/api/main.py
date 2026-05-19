"""FastAPI application factory and HTTP routes.

The HTTP layer is a thin adapter: it validates input, delegates to the
application service, maps domain errors to HTTP status codes, and
serializes responses. No business logic lives here.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status

from taskflow_ref.api.schemas import CreateTaskRequest, TaskResponse
from taskflow_ref.application.service import TaskNotFoundError, TaskService
from taskflow_ref.composition import build_task_service
from taskflow_ref.infrastructure.settings import Settings
from taskflow_ref.observability.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure a FastAPI application instance.

    Best practices demonstrated:
        - Application-factory pattern: returning a fresh ``app`` rather
          than a module-level global lets each test build an isolated
          instance with injected settings, and avoids import-time side
          effects.
        - Settings are injectable (``settings | None``) with an
          environment fallback, so tests pass explicit config while
          production reads the environment.
        - Composition happens once at startup via ``build_task_service``
          (composition root), not inside request handlers.

    Args:
        settings: Optional explicit settings; falls back to
            ``Settings.from_env()`` when omitted.

    Returns:
        A fully wired ``FastAPI`` application.
    """
    configure_logging()
    resolved_settings = settings or Settings.from_env()
    service = build_task_service(resolved_settings)

    app = FastAPI(title="TaskFlow Reference API", version="0.1.0")

    def get_service() -> TaskService:
        """Dependency provider yielding the shared ``TaskService``.

        Used with ``Depends`` so routes receive the service by
        injection; tests can override this provider to swap in fakes
        without monkeypatching.
        """
        return service

    @app.get("/health")
    def health() -> dict[str, str]:
        """Liveness probe.

        A dedicated, dependency-free health endpoint is a standard
        operational practice for load balancers and orchestrators.
        """
        return {"status": "ok"}

    @app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create_task(
        request: CreateTaskRequest,
        task_service: TaskService = Depends(get_service),
    ) -> TaskResponse:
        """Create a task.

        Best practices demonstrated:
            - Correct REST semantics: ``201 Created`` for resource
              creation via ``status_code``.
            - The body is validated into ``CreateTaskRequest`` before
              the handler runs; the route only translates and delegates
              to the service.
            - ``response_model`` enforces the output schema and strips
              unexpected fields.
        """
        task = task_service.create_task(title=request.title, priority=request.priority)
        return TaskResponse.from_domain(task)

    @app.get("/tasks", response_model=list[TaskResponse])
    def list_tasks(task_service: TaskService = Depends(get_service)) -> list[TaskResponse]:
        """List all tasks.

        Best practices demonstrated:
            - Pure delegation plus an explicit domain→DTO mapping; the
              handler stays trivial and free of business logic.
        """
        return [TaskResponse.from_domain(task) for task in task_service.list_tasks()]

    @app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
    def complete_task(
        task_id: UUID,
        task_service: TaskService = Depends(get_service),
    ) -> TaskResponse:
        """Complete a task by id.

        Best practices demonstrated:
            - ``task_id`` is declared as ``UUID``, so FastAPI parses and
              validates the path parameter (malformed ids → 422).
            - The domain ``TaskNotFoundError`` is translated to a proper
              HTTP 404 here, at the boundary, keeping HTTP concerns out
              of the service layer.
            - ``raise ... from exc`` preserves the exception chain for
              debuggable tracebacks.
        """
        try:
            task = task_service.complete_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return TaskResponse.from_domain(task)

    return app
