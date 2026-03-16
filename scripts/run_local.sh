#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="/tmp/chatgpt-tarot-divination.pid"
LOG_FILE="/tmp/chatgpt-tarot-divination.log"

cd "$ROOT_DIR"

if [[ "${1:-}" == "stop" ]]; then
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    kill "$(cat "$PID_FILE")"
    rm -f "$PID_FILE"
    echo "stopped"
  else
    echo "not running"
  fi
  exit 0
fi

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "already running: pid=$(cat "$PID_FILE")"
  exit 0
fi

nohup .venv/bin/python3 main.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
sleep 1
echo "started: pid=$(cat "$PID_FILE")"
