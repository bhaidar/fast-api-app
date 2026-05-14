from unittest import TestCase

from fastapi.testclient import TestClient

from fast_api_app.main import app, mock_database
from fast_api_app.models import ProjectRead


client = TestClient(app)


def serialize_project(project: ProjectRead) -> dict[str, object]:
    return project.model_dump(mode="json")


def serialize_projects(projects: list[ProjectRead]) -> list[dict[str, object]]:
    return [serialize_project(project) for project in projects]


class ProjectEndpointTests(TestCase):
    def test_mock_database_returns_project_read_models(self) -> None:
        self.assertIsInstance(mock_database()[1], ProjectRead)

    def test_get_projects_returns_all_mock_projects(self) -> None:
        response = client.get("/projects")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), serialize_projects(list(mock_database().values())))

    def test_get_projects_includes_created_at(self) -> None:
        response = client.get("/projects")

        self.assertEqual(response.status_code, 200)
        self.assertIn("created_at", response.json()[0])

    def test_get_projects_filters_by_slug(self) -> None:
        project = mock_database()[1]

        response = client.get("/projects", params={"slug": project.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [serialize_project(project)])

    def test_get_projects_returns_all_projects_for_unknown_slug(self) -> None:
        response = client.get("/projects", params={"slug": "unknown-project"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), serialize_projects(list(mock_database().values())))

    def test_get_project_returns_matching_project(self) -> None:
        project = mock_database()[1]

        response = client.get("/project", params={"project_id": project.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), serialize_project(project))

    def test_get_project_returns_not_found_for_unknown_project(self) -> None:
        response = client.get("/project", params={"project_id": 999999})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Project not found"})
