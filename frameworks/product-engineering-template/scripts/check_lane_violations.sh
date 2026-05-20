#!/usr/bin/env bash
set -euo pipefail

# v10.18 — Detect Stay-in-lane violations.
#
# Scans files modified in the last MINUTES_BACK minutes and matches each
# against the expected owner role. Prints a warning whenever a file's
# expected owner doesn't match what the Orchestrator role is allowed to
# touch directly.
#
# Usage:
#   bash scripts/check_lane_violations.sh [MINUTES_BACK]
#
# Output:
#   - List of recently-modified files
#   - For each: expected owner role
#   - Warning if Orchestrator-touchable list was crossed
#
# This is informational only — does NOT block writes. Use it during/
# after a phase to spot whether the Orchestrator drifted out of its lane.

MINUTES_BACK="${1:-60}"

# Files Orchestrator may write directly (the only ones — everything else
# must be routed to the owner role).
ORCH_ALLOWED=(
  "TASK.md"
  "memory/_PROJECT_STATE.md"
  "memory/ORCHESTRATOR.md"
)

# Map files → owner role.
owner_of() {
  case "$1" in
    TASK.md|memory/_PROJECT_STATE.md|memory/ORCHESTRATOR.md) echo "ORCHESTRATOR" ;;
    PRODUCT_IDEA.md)                                          echo "USER" ;;
    docs/product/PRD.md|docs/product/ROADMAP.md)              echo "PM" ;;
    planning/BACKLOG.md|planning/OPEN_QUESTIONS.md)           echo "PM" ;;
    docs/product/UX_FLOW.md|docs/product/WIREFRAMES.md|docs/product/DESIGN_NOTES.md) echo "UX" ;;
    docs/ux/*)                                                 echo "UX" ;;
    docs/business/*)                                           echo "BA" ;;
    docs/architecture/*)                                       echo "SA" ;;
    backend/*)                                                 echo "BE" ;;
    frontend/*)                                                echo "FE" ;;
    planning/BE_PLAN.md)                                       echo "BE" ;;
    planning/FE_PLAN.md)                                       echo "FE" ;;
    docs/qa/*|reports/*)                                       echo "QA" ;;
    docs/delivery/*|docker-compose*|Dockerfile*)               echo "DELIVERY" ;;
    memory/PM.md)                                              echo "PM" ;;
    memory/SA.md)                                              echo "SA" ;;
    memory/BA.md)                                              echo "BA" ;;
    memory/UX.md)                                              echo "UX" ;;
    memory/BE.md)                                              echo "BE" ;;
    memory/FE.md)                                              echo "FE" ;;
    memory/QA.md)                                              echo "QA" ;;
    memory/DELIVERY.md)                                        echo "DELIVERY" ;;
    *) echo "?" ;;
  esac
}

is_orchestrator_allowed() {
  local f="$1"
  for a in "${ORCH_ALLOWED[@]}"; do
    [[ "$f" == "$a" ]] && return 0
  done
  return 1
}

echo "================================================================"
echo " Lane-violation lint — files modified in the last ${MINUTES_BACK} min"
echo "================================================================"

# Collect recently-modified project files (skip generated/ignored dirs).
MTIME_ARG="-mmin -${MINUTES_BACK}"
FILES=$(find . \
    -type f \
    $MTIME_ARG \
    -not -path '*/\.*' \
    -not -path './node_modules/*' \
    -not -path './.venv/*' \
    -not -path './venv/*' \
    -not -path './__pycache__/*' \
    -not -path './dist/*' \
    -not -path './build/*' \
    -not -path './.framework_sync_backup/*' \
    2>/dev/null | sed 's|^\./||' || true)

if [[ -z "$FILES" ]]; then
  echo "No recently-modified files."
  exit 0
fi

WARN_COUNT=0
OK_COUNT=0
echo
printf "  %-50s  %-12s  %s\n" "FILE" "OWNER" "STATUS"
printf "  %-50s  %-12s  %s\n" "----" "-----" "------"
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  owner=$(owner_of "$f")
  status="ok"
  # Orchestrator-allowed files are always fine.
  if is_orchestrator_allowed "$f"; then
    status="orchestrator-ok"
  fi
  printf "  %-50s  %-12s  %s\n" "${f:0:50}" "$owner" "$status"
  if [[ "$status" == "ok" ]]; then
    OK_COUNT=$((OK_COUNT + 1))
  fi
done <<< "$FILES"

echo
echo "Summary:"
echo "  Files modified: $(echo "$FILES" | wc -l | tr -d ' ')"
echo
echo "Note: this script can't tell WHICH role made each edit (there's no"
echo "per-role audit log yet). It only reports who SHOULD have written"
echo "each file. If you see edits to files outside the Orchestrator's"
echo "allowed list (TASK.md, memory/_PROJECT_STATE.md, memory/ORCHESTRATOR.md)"
echo "right after an Orchestrator turn — and no route_to_pane.sh call"
echo "preceded them — that's a likely Stay-in-lane violation."

# v10.19 — Action-level audit. Scan PATH-guard log + recent shell
# history for engineering commands the Orchestrator may have run
# (or attempted).
echo
echo "================================================================"
echo " Action-level audit (v10.19)"
echo "================================================================"

# Hard-guard hits (Orchestrator attempts blocked at PATH level)
GUARD_LOG="${TMPDIR:-/tmp}/orchestrator_guard.log"
if [[ -f "$GUARD_LOG" ]]; then
  RECENT_BLOCKS=$(tail -n 20 "$GUARD_LOG" 2>/dev/null)
  if [[ -n "$RECENT_BLOCKS" ]]; then
    echo
    echo "Recent PATH-guard blocks (Orchestrator tried engineering commands):"
    echo "$RECENT_BLOCKS" | sed 's/^/  /'
  fi
fi

# Detect engineering processes that ran recently as Orchestrator's child
# (best-effort — uses ps + heuristics).
if [[ -f .agent_panes ]]; then
  ORCH_PANE=$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2-)
  if [[ -n "$ORCH_PANE" ]] && command -v tmux >/dev/null 2>&1; then
    ORCH_PID=$(tmux display-message -p -t "$ORCH_PANE" '#{pane_pid}' 2>/dev/null || true)
    if [[ -n "$ORCH_PID" ]]; then
      # Find all descendants of ORCH_PID and check their cmd names
      DESCENDANTS=$(pgrep -P "$ORCH_PID" 2>/dev/null || true)
      if [[ -n "$DESCENDANTS" ]]; then
        echo
        echo "Live descendants of Orchestrator pane PID=$ORCH_PID:"
        ps -p "$DESCENDANTS" -o pid,comm 2>/dev/null | sed 's/^/  /'
        # Flag any engineering commands among them
        FLAGGED=$(ps -p "$DESCENDANTS" -o comm= 2>/dev/null | grep -E '^(docker|psql|mongo|node|python|pip|npm|yarn|kubectl)' || true)
        if [[ -n "$FLAGGED" ]]; then
          echo
          echo "  ⚠️  Engineering processes running under Orchestrator — likely lane violation in progress."
        fi
      fi
    fi
  fi
fi

echo "================================================================"
