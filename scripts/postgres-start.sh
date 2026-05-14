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
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16}"
POSTGRES_DB="${POSTGRES_DB:-fastapi_app}"
POSTGRES_USER="${POSTGRES_USER:-fastapi}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-fastapi}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_VOLUME="${POSTGRES_VOLUME:-fast-api-app-postgres-data}"

if ! command -v podman >/dev/null 2>&1; then
  echo "podman is required to run the local PostgreSQL container." >&2
  exit 1
fi

if podman container exists "${POSTGRES_CONTAINER_NAME}"; then
  if [[ "$(podman inspect --format '{{.State.Running}}' "${POSTGRES_CONTAINER_NAME}")" == "true" ]]; then
    echo "Container ${POSTGRES_CONTAINER_NAME} is already running."
  else
    podman start "${POSTGRES_CONTAINER_NAME}" >/dev/null
    echo "Started container ${POSTGRES_CONTAINER_NAME}."
  fi
else
  podman volume exists "${POSTGRES_VOLUME}" >/dev/null 2>&1 ||
    podman volume create "${POSTGRES_VOLUME}" >/dev/null

  podman run \
    --detach \
    --name "${POSTGRES_CONTAINER_NAME}" \
    --env "POSTGRES_DB=${POSTGRES_DB}" \
    --env "POSTGRES_USER=${POSTGRES_USER}" \
    --env "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
    --publish "127.0.0.1:${POSTGRES_PORT}:5432" \
    --volume "${POSTGRES_VOLUME}:/var/lib/postgresql/data" \
    "${POSTGRES_IMAGE}" >/dev/null

  echo "Created and started container ${POSTGRES_CONTAINER_NAME}."
fi

printf "Waiting for PostgreSQL to become ready"
for _ in {1..30}; do
  if podman exec "${POSTGRES_CONTAINER_NAME}" \
    pg_isready --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" >/dev/null 2>&1; then
    printf "\nPostgreSQL is ready.\n\n"
    cat <<EOF
Connection settings:
  Host: 127.0.0.1
  Port: ${POSTGRES_PORT}
  Database: ${POSTGRES_DB}
  User: ${POSTGRES_USER}
  Password: ${POSTGRES_PASSWORD}
EOF
    exit 0
  fi

  printf "."
  sleep 1
done

printf "\nPostgreSQL did not become ready within 30 seconds.\n" >&2
podman logs "${POSTGRES_CONTAINER_NAME}" >&2 || true
exit 1
