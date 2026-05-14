from unittest import TestCase

from fast_api_app.models import Project


class ProjectModelTests(TestCase):
    def test_project_model_serializes_project_shape(self) -> None:
        project = Project(id=1, name="Project 1", slug="project-1")

        self.assertEqual(
            project.model_dump(),
            {"id": 1, "name": "Project 1", "slug": "project-1"},
        )
