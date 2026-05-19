# Engineering Notes

## Why this is layered

The goal is not architecture theater. Each layer has a reason:

- `domain`: pure business objects and invariants.
- `application`: use cases. Depends on protocols, not concrete services.
- `infrastructure`: JSON files, HTTP clients, and other side effects.
- `api` and `cli`: thin delivery mechanisms.
- `composition.py`: one obvious place where concrete dependencies are wired.

## Why Pydantic is not everywhere

Pydantic is excellent at process boundaries: API payloads, configuration, persistence records.

Inside the domain, dataclasses are simpler and faster to read.

## Why no IoC container

Python dependency injection is usually just passing objects explicitly.
A framework container would add noise without adding value here.

## File IO example

`JsonTaskRepository` demonstrates safe-ish small-project JSON persistence:

- parent directory creation
- UTF-8 encoding
- validation on read
- domain serialization boundary

For concurrent writes or larger data, use SQLite/Postgres instead.

## HTTP example

`WebhookTaskNotifier` demonstrates:

- explicit timeout
- bounded retries
- error surfacing
- payload serialization at the boundary

## Testing strategy

- Unit tests cover domain/application behavior without files or HTTP.
- Integration tests cover FastAPI, JSON persistence, and HTTP adapter behavior.
- The repository and notifier are replaceable because application code depends on protocols.
