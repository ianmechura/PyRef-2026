from __future__ import annotations

from pathlib import Path
from uuid import UUID

import typer

from taskflow_ref.composition import build_task_service
from taskflow_ref.domain.models import Priority
from taskflow_ref.infrastructure.settings import Settings
from taskflow_ref.observability.logging import configure_logging

app = typer.Typer(help="TaskFlow reference CLI")


def _service(data_file: Path | None) -> object:
    settings = Settings.from_env()
    if data_file is not None:
        settings = settings.model_copy(update={"data_file": data_file})

    return build_task_service(settings)


@app.command()
def create(
    title: str,
    priority: Priority = Priority.NORMAL,
    data_file: Path | None = typer.Option(None, help="Path to JSON task store."),
) -> None:
    configure_logging()
    service = _service(data_file)
    task = service.create_task(title=title, priority=priority)
    typer.echo(f"created {task.id} {task.title}")


@app.command("list")
def list_tasks(
    data_file: Path | None = typer.Option(None, help="Path to JSON task store."),
) -> None:
    service = _service(data_file)
    for task in service.list_tasks():
        typer.echo(f"{task.id} [{task.status}] {task.priority}: {task.title}")


@app.command()
def complete(
    task_id: UUID,
    data_file: Path | None = typer.Option(None, help="Path to JSON task store."),
) -> None:
    configure_logging()
    service = _service(data_file)
    task = service.complete_task(task_id)
    typer.echo(f"completed {task.id} {task.title}")
