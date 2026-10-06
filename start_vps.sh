#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
  else
    echo "Unable to find a Python interpreter. Install Python or create a virtual environment first." >&2
    exit 1
  fi
fi

LOG_FILE="${LOG_FILE:-$PROJECT_DIR/bot.log}"
PID_FILE="${PID_FILE:-$PROJECT_DIR/finance-assistant.pid}"

if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "Warning: .env file not found. Copy .env.example to .env and configure your Telegram token before running the app." >&2
fi

echo "Starting Finance Assistant from $PROJECT_DIR"
echo "Using Python: $PYTHON_BIN"
echo "Logging to: $LOG_FILE"

nohup "$PYTHON_BIN" -m finance_assistant.main > "$LOG_FILE" 2>&1 < /dev/null &
SERVER_PID=$!
printf "%s" "$SERVER_PID" > "$PID_FILE"

echo "Finance Assistant started in the background."
echo "PID: $SERVER_PID"
echo "PID file: $PID_FILE"
echo "Log file: $LOG_FILE"
