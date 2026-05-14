import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from fast_api_app.settings import DEFAULT_DATABASE_URL, Settings, get_settings


class SettingsTests(TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_settings_defaults_to_local_postgres_url(self) -> None:
        settings = Settings(_env_file=None)

        self.assertEqual(settings.database_url, DEFAULT_DATABASE_URL)

    def test_settings_loads_database_url_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.postgres"
            env_file.write_text(
                "DATABASE_URL=postgresql+psycopg://example:example@localhost:5432/example\n",
                encoding="utf-8",
            )

            settings = Settings(_env_file=env_file)

        self.assertEqual(
            settings.database_url,
            "postgresql+psycopg://example:example@localhost:5432/example",
        )

    def test_settings_ignores_empty_database_url_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.postgres"
            env_file.write_text("DATABASE_URL=\n", encoding="utf-8")

            settings = Settings(_env_file=env_file)

        self.assertEqual(settings.database_url, DEFAULT_DATABASE_URL)

    def test_settings_ignores_other_postgres_env_file_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.postgres"
            env_file.write_text(
                "\n".join(
                    [
                        "POSTGRES_CONTAINER_NAME=fast-api-app-postgres",
                        "POSTGRES_IMAGE=postgres:16",
                        "POSTGRES_DB=fastapi_app",
                        "POSTGRES_USER=fastapi",
                        "POSTGRES_PASSWORD=fastapi",
                        "POSTGRES_PORT=5432",
                        "POSTGRES_VOLUME=fast-api-app-postgres-data",
                        (
                            "DATABASE_URL=postgresql+psycopg://example:example"
                            "@localhost:5432/example"
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            settings = Settings(_env_file=env_file)

        self.assertEqual(
            settings.database_url,
            "postgresql+psycopg://example:example@localhost:5432/example",
        )

    def test_environment_database_url_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.postgres"
            env_file.write_text(
                "DATABASE_URL=postgresql+psycopg://file:file@localhost:5432/file\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "DATABASE_URL": (
                        "postgresql+psycopg://env:env@localhost:5432/env"
                    )
                },
            ):
                settings = Settings(_env_file=env_file)

        self.assertEqual(
            settings.database_url,
            "postgresql+psycopg://env:env@localhost:5432/env",
        )

    def test_get_settings_returns_cached_settings(self) -> None:
        first = get_settings()
        second = get_settings()

        self.assertIs(first, second)
