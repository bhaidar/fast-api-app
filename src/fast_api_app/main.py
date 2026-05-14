from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException

from fast_api_app.models import ProjectRead


app = FastAPI(
    title="FastAPI App", description="A simple FastAPI application", version="1.0.0"
)


ProjectData = dict[str, int | str | datetime | None]


def mock_database() -> dict[int, ProjectData]:
    return {
        1: {
            "id": 1,
            "name": "Project 1",
            "slug": "project-1",
            "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        },
        2: {
            "id": 2,
            "name": "Project 2",
            "slug": "project-2",
            "created_at": datetime(2026, 1, 2, tzinfo=UTC),
        },
        3: {
            "id": 3,
            "name": "Project 3",
            "slug": "project-3",
            "created_at": datetime(2026, 1, 3, tzinfo=UTC),
        },
    }


@app.get("/project", response_model=ProjectRead)
def get_project(project_id: int) -> ProjectRead:
    project = mock_database().get(project_id)
    if project is not None:
        return ProjectRead(**project)
    raise HTTPException(status_code=404, detail="Project not found")


@app.get("/projects", response_model=list[ProjectRead])
def get_projects(slug: str | None = None) -> list[ProjectRead]:
    projects = [ProjectRead(**project) for project in mock_database().values()]
    if slug is None:
        return projects

    matching_projects = [project for project in projects if project.slug == slug]
    if matching_projects:
        return matching_projects

    return projects
