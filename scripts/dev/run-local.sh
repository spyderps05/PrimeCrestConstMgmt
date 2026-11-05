#!/usr/bin/env bash
# Start a local PrimeCrest dev stack on non-default ports (backend :8810, frontend :5810).
# - Ensures throwaway PostgreSQL 16 container (primecrest-qa-pg, host port 55432) is running.
# - Backend: uvicorn app.main:create_app --factory on 127.0.0.1:8810. Schema is created on first
#   boot (create_all + alembic stamp); demo accounts/projects seeded when SEED_DEMO=true.
# - Frontend: vite on 127.0.0.1:5810 with /api proxied to :8810 via VITE_API_TARGET.
# Usage: scripts/dev/run-local.sh [--stop]
# Env overrides: BACKEND_PORT FRONTEND_PORT PG_PORT PG_CONTAINER PYTHON
# Demo login: demo@openconstructionerp.com / DemoPass1234!
set -euo pipefail

BACKEND_PORT="${BACKEND_PORT:-8810}"
FRONTEND_PORT="${FRONTEND_PORT:-5810}"
PG_PORT="${PG_PORT:-55432}"
PG_CONTAINER="${PG_CONTAINER:-primecrest-qa-pg}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -z "${PYTHON:-}" ]]; then
  if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then PYTHON="$ROOT/backend/.venv/bin/python"
  elif [[ -x "H:/PrimeCrestConstMgmt/backend/.venv/Scripts/python.exe" ]]; then PYTHON="H:/PrimeCrestConstMgmt/backend/.venv/Scripts/python.exe"
  else PYTHON=python3; fi
fi
LOG_DIR="$ROOT/scripts/dev/.local/logs"
PID_FILE="$LOG_DIR/pids.txt"
mkdir -p "$LOG_DIR"

if [[ "${1:-}" == "--stop" ]]; then
  if [[ -f "$PID_FILE" ]]; then
    while read -r p; do kill "$p" 2>/dev/null || true; done < "$PID_FILE"
    rm -f "$PID_FILE"
  fi
  echo "Stopped dev servers (postgres container '$PG_CONTAINER' left running)."
  exit 0
fi

state="$(docker ps -a --filter "name=^${PG_CONTAINER}\$" --format '{{.State}}' || true)"
if [[ -z "$state" ]]; then
  docker run -d --name "$PG_CONTAINER" -e POSTGRES_USER=primecrest -e POSTGRES_PASSWORD=primecrest \
    -e POSTGRES_DB=primecrest -p "${PG_PORT}:5432" postgres:16 >/dev/null
elif [[ "$state" != "running" ]]; then
  docker start "$PG_CONTAINER" >/dev/null
fi
for _ in $(seq 1 30); do docker exec "$PG_CONTAINER" pg_isready -U primecrest >/dev/null 2>&1 && break; sleep 1; done

export DATABASE_URL="postgresql+asyncpg://primecrest:primecrest@127.0.0.1:${PG_PORT}/primecrest"
export DATABASE_SYNC_URL="postgresql://primecrest:primecrest@127.0.0.1:${PG_PORT}/primecrest"
export SEED_DEMO=true DEMO_USER_PASSWORD='DemoPass1234!' DEMO_ESTIMATOR_PASSWORD='DemoPass1234!' DEMO_MANAGER_PASSWORD='DemoPass1234!'
# OE_CLI_DATA_DIR keeps demo/partner-pack markers per stack (else ~/.openestimate leaks into fresh DBs).
export OE_DATA_DIR="$ROOT/scripts/dev/.local/data" OE_CLI_DATA_DIR="$ROOT/scripts/dev/.local/data" PYTHONIOENCODING=utf-8
export ALLOWED_ORIGINS="http://127.0.0.1:${FRONTEND_PORT},http://localhost:${FRONTEND_PORT}"

(cd "$ROOT/backend" && PYTHONPATH=. nohup "$PYTHON" -m uvicorn app.main:create_app --factory \
  --host 127.0.0.1 --port "$BACKEND_PORT" >"$LOG_DIR/backend.log" 2>&1 & echo $! >"$PID_FILE")

if [[ "${NO_FRONTEND:-0}" != "1" ]]; then
  (cd "$ROOT/frontend" && VITE_API_TARGET="http://127.0.0.1:${BACKEND_PORT}" nohup npx vite --port "$FRONTEND_PORT" \
    --strictPort --host 127.0.0.1 >"$LOG_DIR/frontend.log" 2>&1 & echo $! >>"$PID_FILE")
fi

echo "Waiting for backend on :$BACKEND_PORT (first boot creates schema + seeds demo data)..."
for _ in $(seq 1 600); do curl -fsS "http://127.0.0.1:${BACKEND_PORT}/api/health" >/dev/null 2>&1 && break; sleep 2; done
echo "Backend : http://127.0.0.1:${BACKEND_PORT}  (docs: /api/docs)"
echo "Frontend: http://127.0.0.1:${FRONTEND_PORT}"
echo "Login   : demo@openconstructionerp.com / DemoPass1234!"
echo "Logs    : $LOG_DIR   Stop: scripts/dev/run-local.sh --stop"
