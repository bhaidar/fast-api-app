# FastAPI App

A small FastAPI application packaged with a `src/` layout and managed with
[`uv`](https://docs.astral.sh/uv/). The app exposes mock project data through
two API endpoints and includes endpoint tests built with `unittest` and
FastAPI's `TestClient`.

## What has been created so far

- A Python package project named `fast-api-app`.
- A FastAPI ASGI app at `src/fast_api_app/main.py`.
- A configured FastAPI CLI entrypoint:
  `fast_api_app.main:app`.
- A mock in-memory project database that returns `ProjectRead` models.
- SQLModel project table and API schema models in `src/fast_api_app/models.py`.
- Endpoint tests for project listing, filtering, lookup, and not-found
  behavior.
- A guide in `docs/uv-fastapi-package-guide.md` that documents how the project
  was created.

## Requirements

- Python 3.14
- `uv`
- Podman, when running the local PostgreSQL development database

The repository pins Python with `.python-version` and `pyproject.toml`:

```toml
requires-python = "==3.14.*"
```

## Install dependencies

Sync the project dependencies from `uv.lock`:

```bash
uv sync
```

## Local PostgreSQL with Podman

This repository includes helper scripts for running a local PostgreSQL database
with Podman. The FastAPI app still uses `mock_database()` for endpoint data;
the database is ready for the next integration step.

From the repository root, start the Podman machine if it is not already
running:

```bash
podman machine start
```

Create a local environment file from the safe defaults:

```bash
cp .env.postgres.example .env.postgres
```

Start PostgreSQL:

```bash
scripts/postgres-start.sh
```

Verify the database connection:

```bash
scripts/postgres-shell.sh -c 'select current_database(), current_user;'
```

Open `psql` inside the container:

```bash
scripts/postgres-shell.sh
```

Stop PostgreSQL without deleting its data:

```bash
scripts/postgres-stop.sh
```

The default setup uses:

- Container: `fast-api-app-postgres`
- Image: `postgres:16`
- Database: `fastapi_app`
- User: `fastapi`
- Password: `fastapi`
- Host port: `127.0.0.1:5432`
- Data volume: `fast-api-app-postgres-data`

### Manage the database with TablePlus

Yes, TablePlus is a good choice for managing this local database. Create a new
PostgreSQL connection with these settings:

| Field | Value |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `fastapi_app` |
| User | `fastapi` |
| Password | `fastapi` |

## SQLModel models

The app uses SQLModel in `src/fast_api_app/models.py` for database-ready models
and API schemas. PostgreSQL is available locally through Podman, but the routes
still use typed mock data until the database integration is wired into the app.

- `ProjectName`: constrained string type that trims whitespace and requires at
  least two characters.
- `ProjectBase`: shared project fields used by write models, currently `name`
  and optional `description`.
- `Project`: database table model for the `projects` table, with `id`, unique
  `slug`, and timezone-aware `created_at`.
- `ProjectCreate`: create payload with client-provided `name` and optional
  `description`; `slug` is intentionally omitted because it will be derived from
  the name.
- `ProjectUpdate`: partial update payload where `name`, `description`, and
  `slug` are optional.
- `ProjectRead`: response schema used by the read endpoints, with `id`, `name`,
  `slug`, and `created_at`.

## Run the app

Run the development server with the FastAPI CLI:

```bash
uv run fastapi dev
```

Or run the app directly with Uvicorn:

```bash
uv run uvicorn fast_api_app.main:app --reload
```

Verify that the configured FastAPI entrypoint resolves:

```bash
uv run python -c "from fast_api_app.main import app; print(app.title)"
```

Expected output:

```text
FastAPI App
```

When the server is running locally, the interactive API docs are available at:

- <http://127.0.0.1:8000/docs>
- <http://127.0.0.1:8000/redoc>

## API endpoints

### `GET /projects`

Returns all mock projects.

Optional query parameter:

- `slug`: when it matches a project slug, returns only that project; when it
  does not match, returns all projects.

Example:

```bash
curl "http://127.0.0.1:8000/projects"
curl "http://127.0.0.1:8000/projects?slug=project-1"
```

### `GET /project`

Returns one project by integer project ID.

Required query parameter:

- `project_id`

Example:

```bash
curl "http://127.0.0.1:8000/project?project_id=1"
```

Unknown project IDs return `404` with:

```json
{"detail":"Project not found"}
```

## Run tests

Run the full test suite:

```bash
uv run python -m unittest discover -s tests
```

Run the endpoint test module:

```bash
uv run python -m unittest tests.test_main
```

Run a single endpoint test:

```bash
uv run python -m unittest tests.test_main.ProjectEndpointTests.test_get_project_returns_matching_project
```

No lint command is configured in `pyproject.toml` yet.

## Project structure

```text
.
├── .github/copilot-instructions.md
├── docs/
│   └── uv-fastapi-package-guide.md
├── scripts/
│   ├── postgres-shell.sh
│   ├── postgres-start.sh
│   └── postgres-stop.sh
├── src/
│   └── fast_api_app/
│       ├── __init__.py
│       ├── models.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_models.py
├── .env.postgres.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## Notes

- Keep the ASGI import string as `fast_api_app.main:app` unless the module
  layout changes.
- Keep route `response_model` declarations aligned with the data returned by
  each endpoint because FastAPI validates responses at runtime.
