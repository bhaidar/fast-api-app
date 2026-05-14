import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATABASE_URL = (
    "postgresql+psycopg://fastapi:fastapi@127.0.0.1:5432/fastapi_app"
)


class AlembicMigrationTests(TestCase):
    def run_alembic(
        self, *args: str, database_url: str | None = LOCAL_DATABASE_URL
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if database_url is None:
            env.pop("DATABASE_URL", None)
        else:
            env["DATABASE_URL"] = database_url

        return subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_alembic_requires_database_url(self) -> None:
        result = self.run_alembic("current", database_url=None)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "DATABASE_URL is required to run Alembic migrations",
            result.stderr,
        )

    def test_offline_upgrade_sql_creates_projects_table(self) -> None:
        result = self.run_alembic("upgrade", "head", "--sql")

        self.assertEqual(result.returncode, 0, result.stderr)
        expected_fragments = [
            "CREATE TABLE projects",
            "name VARCHAR NOT NULL",
            "description VARCHAR",
            "id SERIAL NOT NULL",
            "slug VARCHAR NOT NULL",
            "created_at TIMESTAMP WITH TIME ZONE NOT NULL",
            "PRIMARY KEY (id)",
            "UNIQUE (name)",
            "UNIQUE (slug)",
        ]

        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result.stdout)
