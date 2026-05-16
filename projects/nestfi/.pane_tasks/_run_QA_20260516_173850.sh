#!/bin/bash

ROLE='QA'

# v10.18 — Heartbeat: background loop touches the heartbeat file
# every 10s so the watcher_daemon can detect a stalled worker.
mkdir -p .pane_heartbeats
(
  while :; do
    touch ".pane_heartbeats/${ROLE}.beat" 2>/dev/null || true
    sleep 10
  done
) &
HEARTBEAT_PID=$!
trap 'kill $HEARTBEAT_PID 2>/dev/null; rm -f .pane_heartbeats/${ROLE}.beat 2>/dev/null' EXIT

# v10.18 — Capture start time so the auto-notify safety net can
# tell the difference between 'just finished' and 'crashed instantly'.
START_TS=$(date +%s)

# Run the actual worker command.
claude --print --model 'claude-haiku-4-5' "Execute the routed pane task described in .pane_tasks/QA_20260516_173850.md. Read the file, perform the work, update files as needed, and report completion. Do not use internal subagents (the task tool is disabled in .claude/settings.json and AGENTS.md)."
EXIT_CODE=$?

# v10.18 — Safety net: if the worker didn't call notify_orchestrator.sh
# before exiting, fire one ourselves so the Orchestrator doesn't
# stall waiting for a signal that's never coming. Dedup by checking
# whether this role already filed a notify within the last 30s.
NEED_FALLBACK=true
LATEST_NOTIF=$(ls -t .pane_notifications/${ROLE}_*.md 2>/dev/null | head -1 || true)
if [[ -n "$LATEST_NOTIF" ]]; then
  MTIME=$(stat -f %m "$LATEST_NOTIF" 2>/dev/null || stat -c %Y "$LATEST_NOTIF" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$((NOW - MTIME))
  if (( AGE < 30 )); then
    NEED_FALLBACK=false
  fi
fi
if $NEED_FALLBACK; then
  bash scripts/notify_orchestrator.sh "$ROLE" "Engine session exited (code=$EXIT_CODE) without an explicit completion notify. Check artifacts under role's output paths to verify status. (Auto-fired by framework safety net — worker may have legitimately finished without calling notify_orchestrator.sh, or may have crashed.)" || true
fi

exit $EXIT_CODE
