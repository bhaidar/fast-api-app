import os
import subprocess
from pathlib import Path
from unittest import TestCase


ROOT_DIR = Path(__file__).resolve().parents[1]


class PostgreSQLScriptTests(TestCase):
    def test_example_environment_documents_default_connection(self) -> None:
        env_file = ROOT_DIR / ".env.postgres.example"

        self.assertTrue(env_file.is_file(), ".env.postgres.example should exist")

        env_lines = env_file.read_text(encoding="utf-8").splitlines()
        self.assertIn("POSTGRES_CONTAINER_NAME=fast-api-app-postgres", env_lines)
        self.assertIn("POSTGRES_IMAGE=postgres:16", env_lines)
        self.assertIn("POSTGRES_DB=fastapi_app", env_lines)
        self.assertIn("POSTGRES_USER=fastapi", env_lines)
        self.assertIn("POSTGRES_PASSWORD=fastapi", env_lines)
        self.assertIn("POSTGRES_PORT=5432", env_lines)
        self.assertIn("POSTGRES_VOLUME=fast-api-app-postgres-data", env_lines)

    def test_local_environment_file_is_not_tracked(self) -> None:
        gitignore_lines = (ROOT_DIR / ".gitignore").read_text(
            encoding="utf-8"
        ).splitlines()

        self.assertIn(".env.postgres", gitignore_lines)

    def test_postgres_scripts_exist_are_executable_and_have_valid_syntax(self) -> None:
        for script_name in (
            "postgres-start.sh",
            "postgres-stop.sh",
            "postgres-shell.sh",
        ):
            with self.subTest(script=script_name):
                script_path = ROOT_DIR / "scripts" / script_name

                self.assertTrue(script_path.is_file(), f"{script_name} should exist")
                self.assertTrue(
                    os.access(script_path, os.X_OK),
                    f"{script_name} should be executable",
                )

                subprocess.run(
                    ["bash", "-n", str(script_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
