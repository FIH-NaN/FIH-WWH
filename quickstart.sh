#!/bin/bash
# One-command startup for Wealth Wellness Hub (Git Bash / WSL Bash)

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Starting Wealth Wellness Hub..."

VENV_DIR=".venv"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
  ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
else
  ACTIVATE_PATH="$VENV_DIR/bin/activate"
fi

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$ACTIVATE_PATH"

pip install -r src/server/requirements.txt

if [ ! -f "src/server/.env" ] && [ -f "src/server/.env.example" ]; then
  cp src/server/.env.example src/server/.env
fi

cd src/web
npm install
cd "$ROOT_DIR"

cd src/server
python main.py &
BACKEND_PID=$!
cd "$ROOT_DIR"

cd src/web
npm run dev &
FRONTEND_PID=$!
cd "$ROOT_DIR"

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both services"

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM
wait
