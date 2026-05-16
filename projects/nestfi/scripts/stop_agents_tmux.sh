#!/usr/bin/env bash
set -euo pipefail

# v10.14 — Clean shutdown of the agent session:
#   1. Stops the watcher_daemon background process.
#   2. Kills the tmux session.
#
# Usage:
#   bash scripts/stop_agents_tmux.sh [SESSION_NAME]
#
# If SESSION_NAME is omitted, reads it from .agent_session (written by
# start_agents_tmux.sh).

SESSION_NAME="${1:-}"
if [[ -z "$SESSION_NAME" && -f .agent_session ]]; then
  SESSION_NAME="$(grep '^SESSION_NAME=' .agent_session | cut -d= -f2-)"
fi
if [[ -z "$SESSION_NAME" ]]; then
  echo "Usage: bash scripts/stop_agents_tmux.sh <SESSION_NAME>"
  echo "(no .agent_session found; can't auto-detect session name)"
  exit 1
fi

# 1. Stop watcher daemon.
if [[ -f .watcher.pid ]]; then
  WATCHER_PID="$(cat .watcher.pid)"
  if kill -0 "$WATCHER_PID" 2>/dev/null; then
    echo "Stopping watcher_daemon (pid=$WATCHER_PID)..."
    kill "$WATCHER_PID" 2>/dev/null || true
    sleep 0.3
    kill -9 "$WATCHER_PID" 2>/dev/null || true
  fi
  rm -f .watcher.pid
fi

# 2. Kill tmux session.
if command -v tmux >/dev/null 2>&1; then
  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Killing tmux session: $SESSION_NAME"
    tmux kill-session -t "$SESSION_NAME"
  else
    echo "No tmux session named '$SESSION_NAME' is running."
  fi
fi

echo "Done."
