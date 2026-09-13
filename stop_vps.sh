#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PID_FILE="${PID_FILE:-$PROJECT_DIR/finance-assistant.pid}"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file found at $PID_FILE"
  echo "The app may already be stopped or the launcher was not used."
  exit 1
fi

PID="$(cat "$PID_FILE")"

if [ -z "$PID" ]; then
  echo "PID file is empty: $PID_FILE"
  exit 1
fi

if ! kill -0 "$PID" >/dev/null 2>&1; then
  echo "Process $PID is not running. Removing stale PID file."
  rm -f "$PID_FILE"
  exit 0
fi

kill "$PID"
echo "Stopped Finance Assistant process with PID $PID"
rm -f "$PID_FILE"
