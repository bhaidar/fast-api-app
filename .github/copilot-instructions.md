# Copilot instructions for this repository

## Commands

- Install/sync dependencies: `uv sync`
- Run the development server with the FastAPI CLI: `uv run fastapi dev`
- Run the app directly with Uvicorn: `uv run uvicorn fast_api_app.main:app --reload`
- Verify the configured FastAPI entrypoint resolves:
  `uv run python -c "from fast_api_app.main import app; print(app.title)"`
- Run all tests: `uv run python -m unittest discover -s tests`
- Run the endpoint test module: `uv run python -m unittest tests.test_main`
- Run a single endpoint test:
  `uv run python -m unittest tests.test_main.ProjectEndpointTests.test_get_project_returns_matching_project`

No lint commands are configured in `pyproject.toml` yet.

## Architecture

This is a minimal FastAPI application packaged with a `src/` layout. The ASGI app lives in `src/fast_api_app/main.py` as `app`, and `pyproject.toml` points the FastAPI CLI at it with:

```toml
[tool.fastapi]
entrypoint = "fast_api_app.main:app"
```

The package `src/fast_api_app/__init__.py` is intentionally empty, so do not use `fast_api_app:app` or `main:app` unless the module layout changes. The correct import string is `fast_api_app.main:app`.

Routes and response models currently live together in `main.py`:

- `Project` is a Pydantic model used as the route response shape.
- `mock_database()` returns project records keyed by integer project ID for direct lookup.
- `GET /project` returns one `Project` based on a `project_id` query parameter.
- `GET /projects` returns a list of projects.

## Repository conventions

- Use `uv` for dependency management and command execution; the lockfile is `uv.lock`.
- The project requires Python `3.14` via `.python-version` and `requires-python = "==3.14.*"`.
- Keep route `response_model` declarations aligned with actual response data. FastAPI validates responses against these models, so mismatches can surface as runtime 500 errors.
- When adding modules, keep imports compatible with the `src/` package layout and update `[tool.fastapi].entrypoint` if the ASGI app moves.
