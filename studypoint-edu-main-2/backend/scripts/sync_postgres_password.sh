#!/usr/bin/env sh

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BACKEND_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$BACKEND_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to sync the Postgres password."
  exit 1
fi

echo "Starting postgres service if needed..."
docker compose up -d postgres >/dev/null

retries="${SYNC_POSTGRES_RETRIES:-30}"
delay="${SYNC_POSTGRES_DELAY_SEC:-2}"
i=1
while [ "$i" -le "$retries" ]; do
  if docker compose exec -T postgres sh -lc 'pg_isready -U "${POSTGRES_USER:-postgres}" -d postgres >/dev/null 2>&1'; then
    break
  fi

  echo "Waiting for postgres to accept connections ($i/$retries)..."
  sleep "$delay"
  i=$((i + 1))
done

if [ "$i" -gt "$retries" ]; then
  echo "Postgres did not become ready in time."
  exit 1
fi

echo "Syncing Postgres role password from POSTGRES_* env..."
docker compose exec -T postgres sh -lc '
  password_escaped=$(printf "%s" "${POSTGRES_PASSWORD:-postgres}" | sed "s/'"'"'/''/g")
  psql -v ON_ERROR_STOP=1 \
    -U "${POSTGRES_USER:-postgres}" \
    -d postgres \
    -c "ALTER USER \"${POSTGRES_USER:-postgres}\" WITH PASSWORD '\''${password_escaped}'\'';"
'

echo "Ensuring target database exists..."
docker compose exec -T postgres sh -lc '
  db_name="${POSTGRES_DB:-ixl}"
  if ! psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-postgres}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '\''${db_name}'\'';" | grep -q 1; then
    psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-postgres}" -d postgres -c "CREATE DATABASE \"${db_name}\";"
  fi
'

echo "Postgres credentials are aligned with POSTGRES_* env."
