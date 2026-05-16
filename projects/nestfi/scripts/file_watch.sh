#!/usr/bin/env bash
set -euo pipefail

# v10.14 — Register a "watch": when WAIT_FOR file appears on disk with
# non-empty content, the watcher_daemon will auto-reroute ROLE with
# the stored TASK message. No user intervention required.
#
# A worker uses this when it discovers a missing upstream input
# (typically via check_prerequisites.sh) and wants to be automatically
# resumed when the upstream owner produces the file. Pair with
# notify_orchestrator.sh so the user/Orchestrator also know you are
# parked.
#
# Usage:
#   bash scripts/file_watch.sh <ROLE> <WAIT_FOR_FILE> "<resume task message>"
#
# Example:
#   bash scripts/file_watch.sh UX docs/product/PRD.md \
#     "Resume: PRD is now available. Re-read it, then write docs/product/UX_FLOW.md."

ROLE="${1:-}"
WAIT_FOR="${2:-}"
TASK="${3:-}"

if [[ -z "$ROLE" || -z "$WAIT_FOR" || -z "$TASK" ]]; then
  echo "Usage: bash scripts/file_watch.sh <ROLE> <WAIT_FOR_FILE> \"<resume task>\""
  echo "Roles: PM SA BA UX BE FE QA DELIVERY"
  exit 1
fi

case "$ROLE" in
  PM|SA|BA|UX|BE|FE|QA|DELIVERY) ;;
  *)
    echo "Unknown role: $ROLE"
    exit 1
    ;;
esac

mkdir -p .pane_watches

TS="$(date +%Y%m%d_%H%M%S)"
WATCH_FILE=".pane_watches/${ROLE}_${TS}.watch"

# Escape task message — store as base64 to survive any quoting issues
# during the daemon's eventual reroute call.
TASK_B64="$(printf '%s' "$TASK" | base64 | tr -d '\n')"

cat > "$WATCH_FILE" <<EOF
ROLE="$ROLE"
WAIT_FOR="$WAIT_FOR"
TASK_B64="$TASK_B64"
CREATED_AT="$(date '+%Y-%m-%d %H:%M:%S')"
STATUS="PENDING"
EOF

LOG=".pane_watches/_log.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] REGISTERED $ROLE waiting for $WAIT_FOR" >> "$LOG"

echo "================================================================"
echo " WATCH REGISTERED"
echo "================================================================"
echo " Role     : $ROLE"
echo " Wait for : $WAIT_FOR"
echo " Resume   : $TASK"
echo " File     : $WATCH_FILE"
echo
echo " The watcher_daemon will auto-reroute $ROLE when $WAIT_FOR is"
echo " written by its upstream owner. No user action required."
echo "================================================================"
