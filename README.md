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
- A mock in-memory project database.
- A `Project` Pydantic response model.
- Endpoint tests for project listing, filtering, lookup, and not-found
  behavior.
- A guide in `docs/uv-fastapi-package-guide.md` that documents how the project
  was created.

## Requirements

- Python 3.14
- `uv`

The repository pins Python with `.python-version` and `pyproject.toml`:

```toml
requires-python = "==3.14.*"
```

## Install dependencies

Sync the project dependencies from `uv.lock`:

```bash
uv sync
```

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
├── src/
│   └── fast_api_app/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Notes

- Keep the ASGI import string as `fast_api_app.main:app` unless the module
  layout changes.
- Keep route `response_model` declarations aligned with the data returned by
  each endpoint because FastAPI validates responses at runtime.
