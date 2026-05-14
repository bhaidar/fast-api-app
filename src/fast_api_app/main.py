from fastapi import FastAPI, HTTPException

from fast_api_app.models import Project


app = FastAPI(
    title="FastAPI App", description="A simple FastAPI application", version="1.0.0"
)


ProjectData = dict[str, int | str | None]


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
def get_projects(slug: str | None = None) -> list[Project]:
    projects = [Project(**project) for project in mock_database().values()]
    if slug is None:
        return projects

    matching_projects = [project for project in projects if project.slug == slug]
    if matching_projects:
        return matching_projects

    return projects
