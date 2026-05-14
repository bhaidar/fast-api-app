from datetime import UTC
from unittest import TestCase

from pydantic import ValidationError

from fast_api_app.models import Project, ProjectCreate, ProjectRead, ProjectUpdate


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

    def test_project_create_serializes_create_payload_shape(self) -> None:
        project = ProjectCreate(
            name="Project 1",
            description="Demo project",
            slug="project-1",
        )

        self.assertEqual(
            project.model_dump(),
            {
                "name": "Project 1",
                "description": "Demo project",
                "slug": "project-1",
            },
        )

    def test_project_create_requires_name_and_slug(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectCreate(description="Missing name and slug")

    def test_project_update_serializes_only_set_fields(self) -> None:
        update = ProjectUpdate(name="  Project 1 renamed  ")

        self.assertEqual(
            update.model_dump(exclude_unset=True),
            {"name": "Project 1 renamed"},
        )

    def test_project_update_accepts_nullable_description(self) -> None:
        update = ProjectUpdate(description=None)

        self.assertEqual(
            update.model_dump(exclude_unset=True),
            {"description": None},
        )
