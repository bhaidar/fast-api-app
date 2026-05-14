# Create a FastAPI Package with uv

This guide shows how to create a packaged FastAPI app with `uv`, install `fastapi[standard]`, configure the FastAPI CLI entrypoint, run the app, and run endpoint tests.

## 1. Create a uv package project

Create a new package-style project:

```bash
uv init --package fast-api-app
cd fast-api-app
```

This creates a `pyproject.toml` and a `src/` package layout. A package layout keeps import paths explicit, which matters when running Uvicorn.

## 2. Add FastAPI standard dependencies

Install FastAPI with the standard extras:

```bash
uv add "fastapi[standard]"
```

The standard extras include the FastAPI CLI and Uvicorn-related runtime dependencies. After adding it, `pyproject.toml` should include a dependency like:

```toml
[project]
dependencies = [
    "fastapi[standard]>=0.115.0",
]
```

## 3. Create the FastAPI app module

For this repository, the app lives in:

```text
src/fast_api_app/main.py
```

Example app:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ProjectData = dict[str, int | str | None]


class Project(BaseModel):
    id: int
    name: str
    slug: str | None = None


app = FastAPI(
    title="FastAPI App", description="A simple FastAPI application", version="1.0.0"
)


def mock_database() -> dict[int, ProjectData]:
    return {
        1: {"id": 1, "name": "Project 1", "slug": "project-1"},
        2: {"id": 2, "name": "Project 2", "slug": "project-2"},
        3: {"id": 3, "name": "Project 3", "slug": "project-3"},
    }


@app.get("/project", response_model=Project)
def get_project(project_id: int) -> Project:
    project = mock_database().get(project_id)
    if project is not None:
        return Project(**project)
    raise HTTPException(status_code=404, detail="Project not found")


@app.get("/projects", response_model=list[Project])
def get_projects() -> list[Project]:
    return [Project(**project) for project in mock_database().values()]
```

## 4. Configure the FastAPI CLI entrypoint

Add the FastAPI entrypoint to `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "fast_api_app.main:app"
```

The entrypoint format is:

```text
python.module.path:fastapi_app_variable
```

For this project:

```text
fast_api_app.main:app
```

means:

- import the Python module `fast_api_app.main`
- load the FastAPI object named `app`

Do not use `main:app` unless `main.py` is at the project root. In this repository, `main.py` is inside the package at `src/fast_api_app/main.py`.

## 5. Run the app

Run with the FastAPI CLI:

```bash
uv run fastapi dev
```

Or run directly with Uvicorn:

```bash
uv run uvicorn fast_api_app.main:app --reload
```

Verify the app imports correctly:

```bash
uv run python -c "from fast_api_app.main import app; print(app.title)"
```

Expected output:

```text
FastAPI App
```

## 6. Test endpoints with TestClient

This repository uses Python's built-in `unittest` plus FastAPI's `TestClient`, so no separate pytest dependency is required.

Test file:

```text
tests/test_main.py
```

Example:

```python
from unittest import TestCase

from fastapi.testclient import TestClient

from fast_api_app.main import app, mock_database


client = TestClient(app)


class ProjectEndpointTests(TestCase):
    def test_get_projects_returns_all_mock_projects(self) -> None:
        response = client.get("/projects")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), list(mock_database().values()))

    def test_get_project_returns_matching_project(self) -> None:
        project = mock_database()[1]

        response = client.get("/project", params={"project_id": project["id"]})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), project)

    def test_get_project_returns_not_found_for_unknown_project(self) -> None:
        response = client.get("/project", params={"project_id": 999999})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Project not found"})
```

Run all tests:

```bash
uv run python -m unittest discover -s tests
```

Run the endpoint test module:

```bash
uv run python -m unittest tests.test_main
```

Run a single test:

```bash
uv run python -m unittest tests.test_main.ProjectEndpointTests.test_get_project_returns_matching_project
```
