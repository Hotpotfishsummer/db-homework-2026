#!/bin/sh

# Use separate set calls to avoid compatibility issues with some /bin/sh variants
set -e
set -u

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-60}"

python - <<'PY'
import os
import socket
import time

host = os.getenv("DB_HOST", "postgres")
port = int(os.getenv("DB_PORT", "5432"))
timeout = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
deadline = time.time() + timeout

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Database is reachable at {host}:{port}")
            break
    except OSError:
        if time.time() >= deadline:
            raise SystemExit(f"Timed out waiting for database at {host}:{port}")
        time.sleep(1)
PY

alembic -c db/alembic.ini upgrade heads

exec "$@"