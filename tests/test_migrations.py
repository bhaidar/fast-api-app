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

    def write_env_postgres(self, database_url: str) -> None:
        self.env_file = PROJECT_ROOT / ".env.postgres"
        self.original_env_file = (
            self.env_file.read_text(encoding="utf-8")
            if self.env_file.exists()
            else None
        )
        self.env_file.write_text(f"DATABASE_URL={database_url}\n", encoding="utf-8")

    def tearDown(self) -> None:
        env_file = getattr(self, "env_file", None)
        if env_file is None:
            return

        original_env_file = getattr(self, "original_env_file", None)
        if original_env_file is None:
            env_file.unlink(missing_ok=True)
        else:
            env_file.write_text(original_env_file, encoding="utf-8")

    def assert_creates_projects_table(self, sql: str) -> None:
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
                self.assertIn(fragment, sql)

    def test_offline_upgrade_sql_creates_projects_table(self) -> None:
        result = self.run_alembic("upgrade", "head", "--sql")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_creates_projects_table(result.stdout)

    def test_offline_upgrade_sql_uses_default_database_url_without_export(self) -> None:
        result = self.run_alembic("upgrade", "head", "--sql", database_url=None)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_creates_projects_table(result.stdout)

    def test_alembic_loads_database_url_from_env_postgres(self) -> None:
        self.write_env_postgres(
            "postgresql+psycopg://envfile:envfile@127.0.0.1:5432/envfile"
        )

        result = self.run_alembic("upgrade", "head", "--sql", database_url=None)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_creates_projects_table(result.stdout)
