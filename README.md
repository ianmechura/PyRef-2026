# TaskFlow Reference

A small but non-trivial Python reference project showing modern application-engineering practices:

- `src/` layout
- domain/application/infrastructure separation
- Pydantic models at boundaries
- dataclasses/enums for internal domain state
- structural typing with `Protocol`
- FastAPI HTTP API
- Typer CLI
- JSON file repository
- outbound HTTP adapter with timeout/retry behavior
- structured logging
- pytest unit and integration tests
- Ruff, Pyright, and coverage-friendly project config

The example domain is intentionally simple: a task workflow service that can create tasks, complete them, persist them to disk, and optionally notify a remote webhook.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
pyright
```

Run the API:

```bash
uvicorn taskflow_ref.api.main:create_app --factory --reload
```

Run the CLI:

```bash
taskflow create "Calibrate probe" --priority high
taskflow list
taskflow complete <TASK_ID>
```

## Design rules demonstrated

The API and CLI are thin entry points. They call application services.

Application services depend on protocols, not concrete infrastructure.

Infrastructure implements file IO and HTTP details.

Domain objects do not know about FastAPI, Typer, HTTP, JSON files, or logging.

This project is deliberately small enough to read in one sitting.
