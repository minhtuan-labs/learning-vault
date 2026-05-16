#!/usr/bin/env bash
# v10.14 — Background daemon for continuous orchestration.
#
# Polls .pane_watches/*.watch every POLL_INTERVAL seconds. When the
# WAIT_FOR file referenced by a watch exists on disk AND is non-empty,
# auto-reroutes the parked role with the stored task message, then
# archives the watch.
#
# Started by scripts/start_agents_tmux.sh in the background. PID is
# written to .watcher.pid. Stop with:
#     kill "$(cat .watcher.pid)"
#
# Tuning:
#   POLL_INTERVAL  seconds between polls (default 15)
#   WATCHER_AUTOREROUTE  "true" (default) to auto-reroute. Set "false"
#                        to just log unlocks without rerouting.
#
# Logs to .pane_watches/_log.log so the user can audit what fired
# autonomously.

set -uo pipefail   # NOT -e: a transient sub-script failure must not kill the loop.

POLL_INTERVAL="${POLL_INTERVAL:-15}"
WATCHER_AUTOREROUTE="${WATCHER_AUTOREROUTE:-true}"
LOG=".pane_watches/_log.log"

mkdir -p .pane_watches

echo "================================================================" >> "$LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] watcher_daemon started (pid=$$, poll=${POLL_INTERVAL}s, autoreroute=${WATCHER_AUTOREROUTE})" >> "$LOG"
echo "================================================================" >> "$LOG"

# Graceful shutdown on signals.
trap 'echo "[$(date "+%Y-%m-%d %H:%M:%S")] watcher_daemon stopping (signal received)" >> "$LOG"; exit 0' SIGTERM SIGINT

while true; do
  # Scan all PENDING watches.
  shopt -s nullglob
  for watch in .pane_watches/*.watch; do
    [[ -f "$watch" ]] || continue

    ROLE=""
    WAIT_FOR=""
    TASK_B64=""
    STATUS=""
    # shellcheck disable=SC1090
    source "$watch" 2>/dev/null || continue

    [[ "${STATUS:-}" == "PENDING" ]] || continue
    [[ -n "$ROLE" && -n "$WAIT_FOR" && -n "$TASK_B64" ]] || continue

    # Has the awaited file landed with substantive content?
    if [[ -f "$WAIT_FOR" ]]; then
      sz=$(wc -c < "$WAIT_FOR" 2>/dev/null | tr -d ' ')
      if [[ -n "$sz" ]] && (( sz > 0 )); then
        TASK="$(printf '%s' "$TASK_B64" | base64 -d 2>/dev/null || echo "<task decode failed>")"

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] UNLOCK $ROLE — $WAIT_FOR ready (${sz}B)" >> "$LOG"

        # Atomically flip STATUS so even if we're killed mid-reroute,
        # the next daemon launch doesn't re-fire this watch.
        tmp="${watch}.tmp"
        sed 's/^STATUS="PENDING"/STATUS="TRIGGERED"/' "$watch" > "$tmp" && mv "$tmp" "$watch"

        if [[ "$WATCHER_AUTOREROUTE" == "true" ]]; then
          # Reroute the parked worker with its original task. route_to_pane.sh
          # writes the task file and sends-keys into the worker pane, which
          # boots a fresh engine session there to execute it.
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] REROUTE -> route_to_pane.sh $ROLE \"$TASK\"" >> "$LOG"
          bash scripts/route_to_pane.sh "$ROLE" "$TASK" >> "$LOG" 2>&1 || \
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN route_to_pane.sh $ROLE failed" >> "$LOG"

          # Also notify the Orchestrator so the user sees autonomous activity.
          bash scripts/notify_orchestrator.sh "$ROLE" \
            "Auto-resumed by watcher_daemon — dependency $WAIT_FOR is now ready; resuming original task." \
            >> "$LOG" 2>&1 || true
        else
          echo "[$(date '+%Y-%m-%d %H:%M:%S')] SKIP reroute (WATCHER_AUTOREROUTE=false). Would have routed $ROLE." >> "$LOG"
        fi

        # Archive the watch so it doesn't get re-scanned.
        mv "$watch" "${watch}.done" 2>/dev/null || true
      fi
    fi
  done
  shopt -u nullglob

  sleep "$POLL_INTERVAL"
done
