"""Command-line interface.

Like the HTTP API, the CLI is a thin delivery adapter over the same
application service — proving the core is decoupled from any single
entry point.
"""

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
    """Build a task service for one CLI invocation.

    Best practices demonstrated:
        - Private helper (leading underscore) factoring out the
          composition shared by every command (DRY).
        - Settings come from the environment, with an optional
          per-invocation override applied immutably via
          ``model_copy(update=...)`` rather than mutating the model.

    Args:
        data_file: Optional store path overriding the configured one.

    Returns:
        A configured task service.
    """
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
    """Create a task.

    Best practices demonstrated:
        - Typer derives a typed, self-documenting CLI from the function
          signature; the ``Priority`` enum becomes a validated choice
          and ``--help`` is generated automatically.
        - Logging is configured at the entry point, not at import time.
        - The command only parses args and delegates to the service.
    """
    configure_logging()
    service = _service(data_file)
    task = service.create_task(title=title, priority=priority)
    typer.echo(f"created {task.id} {task.title}")


@app.command("list")
def list_tasks(
    data_file: Path | None = typer.Option(None, help="Path to JSON task store."),
) -> None:
    """List all tasks.

    Best practices demonstrated:
        - Explicit command name (``"list"``) decouples the user-facing
          verb from the Python function name, avoiding a shadow of the
          builtin ``list`` while keeping the CLI readable.
    """
    service = _service(data_file)
    for task in service.list_tasks():
        typer.echo(f"{task.id} [{task.status}] {task.priority}: {task.title}")


@app.command()
def complete(
    task_id: UUID,
    data_file: Path | None = typer.Option(None, help="Path to JSON task store."),
) -> None:
    """Complete a task by id.

    Best practices demonstrated:
        - ``task_id: UUID`` makes Typer validate and convert the
          argument, rejecting malformed ids before any work begins.
        - Consistent thin-adapter shape mirrors the other commands.
    """
    configure_logging()
    service = _service(data_file)
    task = service.complete_task(task_id)
    typer.echo(f"completed {task.id} {task.title}")
