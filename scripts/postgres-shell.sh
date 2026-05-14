#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.postgres"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  source "${ENV_FILE}"
  set +a
fi

POSTGRES_CONTAINER_NAME="${POSTGRES_CONTAINER_NAME:-fast-api-app-postgres}"
POSTGRES_DB="${POSTGRES_DB:-fastapi_app}"
POSTGRES_USER="${POSTGRES_USER:-fastapi}"

if ! command -v podman >/dev/null 2>&1; then
  echo "podman is required to open the local PostgreSQL shell." >&2
  exit 1
fi

if ! podman container exists "${POSTGRES_CONTAINER_NAME}"; then
  echo "Container ${POSTGRES_CONTAINER_NAME} does not exist. Run scripts/postgres-start.sh first." >&2
  exit 1
fi

if [[ "$(podman inspect --format '{{.State.Running}}' "${POSTGRES_CONTAINER_NAME}")" != "true" ]]; then
  echo "Container ${POSTGRES_CONTAINER_NAME} is not running. Run scripts/postgres-start.sh first." >&2
  exit 1
fi

if [[ $# -eq 0 && -t 0 && -t 1 ]]; then
  exec podman exec --interactive --tty "${POSTGRES_CONTAINER_NAME}" \
    psql --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}"
fi

exec podman exec --interactive "${POSTGRES_CONTAINER_NAME}" \
  psql --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" "$@"
