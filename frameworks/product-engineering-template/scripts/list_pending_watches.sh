#!/usr/bin/env bash
set -euo pipefail

# v10.14 — List all PENDING watches so the Orchestrator can tell the
# user which roles are parked waiting for dependencies. Called at the
# start of every Orchestrator turn alongside list_pending_questions.sh.
#
# Usage:
#   bash scripts/list_pending_watches.sh

if [[ ! -d .pane_watches ]]; then
  echo "No watches registered."
  exit 0
fi

PENDING=()
DONE=()

shopt -s nullglob
for w in .pane_watches/*.watch; do
  ROLE=""
  WAIT_FOR=""
  CREATED_AT=""
  STATUS=""
  # shellcheck disable=SC1090
  source "$w" 2>/dev/null || continue

  case "${STATUS:-}" in
    PENDING)
      PENDING+=("${ROLE}|${WAIT_FOR}|${CREATED_AT}|$w")
      ;;
    TRIGGERED)
      DONE+=("${ROLE}|${WAIT_FOR}|${CREATED_AT}|$w")
      ;;
  esac
done
shopt -u nullglob

if [[ ${#PENDING[@]} -eq 0 && ${#DONE[@]} -eq 0 ]]; then
  echo "No active watches."
  exit 0
fi

echo "================================================================"
echo " WATCH STATUS (continuous orchestration)"
echo "================================================================"

if [[ ${#PENDING[@]} -gt 0 ]]; then
  echo
  echo " PENDING (parked, waiting for upstream file):"
  for entry in "${PENDING[@]}"; do
    IFS='|' read -r role wait_for created_at file <<<"$entry"
    echo "   - $role waiting for $wait_for  (since $created_at)"
  done
fi

if [[ ${#DONE[@]} -gt 0 ]]; then
  echo
  echo " TRIGGERED-IN-FLIGHT (file landed, reroute mid-flight):"
  for entry in "${DONE[@]}"; do
    IFS='|' read -r role wait_for created_at file <<<"$entry"
    echo "   - $role  (was waiting for $wait_for)"
  done
fi

# Show recent daemon log activity (last 5 entries) so the Orchestrator
# can mention "watcher just auto-resumed X" to the user.
if [[ -f .pane_watches/_log.log ]]; then
  echo
  echo " Recent watcher activity (last 5):"
  tail -n 5 .pane_watches/_log.log | sed 's/^/   /'
fi

echo "================================================================"
