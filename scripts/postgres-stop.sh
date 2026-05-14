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

if ! command -v podman >/dev/null 2>&1; then
  echo "podman is required to stop the local PostgreSQL container." >&2
  exit 1
fi

if ! podman container exists "${POSTGRES_CONTAINER_NAME}"; then
  echo "Container ${POSTGRES_CONTAINER_NAME} does not exist."
  exit 0
fi

if [[ "$(podman inspect --format '{{.State.Running}}' "${POSTGRES_CONTAINER_NAME}")" == "true" ]]; then
  podman stop "${POSTGRES_CONTAINER_NAME}" >/dev/null
  echo "Stopped container ${POSTGRES_CONTAINER_NAME}."
else
  echo "Container ${POSTGRES_CONTAINER_NAME} is already stopped."
fi
