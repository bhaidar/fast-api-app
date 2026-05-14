from datetime import UTC
from unittest import TestCase

from pydantic import ValidationError

from fast_api_app.models import Project, ProjectRead


class ProjectModelTests(TestCase):
    def test_project_read_serializes_api_response_shape(self) -> None:
        project = ProjectRead(id=1, name="Project 1", slug="project-1")

        self.assertEqual(
            project.model_dump(),
            {"id": 1, "name": "Project 1", "slug": "project-1"},
        )

    def test_project_table_metadata(self) -> None:
        table = Project.__table__

        self.assertEqual(Project.__tablename__, "projects")
        self.assertTrue(table.columns.id.primary_key)
        self.assertTrue(table.columns.name.unique)
        self.assertTrue(table.columns.slug.unique)
        self.assertTrue(table.columns.description.nullable)
        self.assertFalse(table.columns.created_at.nullable)
        self.assertTrue(table.columns.created_at.type.timezone)

    def test_project_defaults_created_at_to_timezone_aware_datetime(self) -> None:
        project = Project(name="Project 1", slug="project-1", description="Demo")

        self.assertIsNone(project.id)
        self.assertEqual(project.description, "Demo")
        self.assertIsNotNone(project.created_at)
        self.assertIs(project.created_at.tzinfo, UTC)

    def test_project_name_strips_whitespace(self) -> None:
        project = ProjectRead(id=1, name="  Project 1  ", slug="project-1")

        self.assertEqual(project.name, "Project 1")

    def test_project_name_requires_at_least_two_characters(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectRead(id=1, name="P", slug="project-1")
