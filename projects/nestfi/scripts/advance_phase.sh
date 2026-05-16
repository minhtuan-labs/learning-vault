#!/usr/bin/env bash
set -euo pipefail

# v10.9 — Officially advance the project to a new phase.
#
# Usage:
#   bash scripts/advance_phase.sh <NEW_PHASE>
#
# Behavior:
#   1. Runs check_phase_gate.sh --through <PREV_PHASE> to verify the
#      team has actually completed everything up to <NEW_PHASE>.
#   2. If the gate fails, refuses to advance and lists the missing
#      items so the Orchestrator knows what to route upstream.
#   3. If the gate passes, updates:
#        - TASK.md "Current Phase" line
#        - memory/_PROJECT_STATE.md current phase + checkbox
#        - appends a Session log line
#
# Override (use sparingly, only when the user explicitly accepts the
# risk):
#   ADVANCE_PHASE_FORCE=1 bash scripts/advance_phase.sh <NEW_PHASE>

NEW_PHASE="${1:-}"
if [[ -z "$NEW_PHASE" ]]; then
  echo "Usage: bash scripts/advance_phase.sh <NEW_PHASE>"
  echo "Phases: 0_DISCOVERY 1_SOLUTION_DESIGN 2_BACKLOG_AND_SPEC"
  echo "        3_IMPLEMENTATION_PLANNING 4_BUILD 5_TEST_AND_FIX 6_DELIVERY"
  exit 2
fi

PHASES=(
  "0_DISCOVERY"
  "1_SOLUTION_DESIGN"
  "2_BACKLOG_AND_SPEC"
  "3_IMPLEMENTATION_PLANNING"
  "4_BUILD"
  "5_TEST_AND_FIX"
  "6_DELIVERY"
)

# Find index of NEW_PHASE
new_idx=-1
for i in "${!PHASES[@]}"; do
  if [[ "${PHASES[$i]}" == "$NEW_PHASE" ]]; then
    new_idx=$i
    break
  fi
done
if (( new_idx < 0 )); then
  echo "Unknown phase: $NEW_PHASE"
  echo "Phases: ${PHASES[*]}"
  exit 2
fi

# Determine prior phase to gate-check
if (( new_idx == 0 )); then
  echo "Advancing to the FIRST phase ($NEW_PHASE). No gate to check."
  GATE_OK=true
else
  prev_idx=$(( new_idx - 1 ))
  prev_phase="${PHASES[$prev_idx]}"
  echo "Gate check: every phase 0..${prev_phase} must be COMPLETE before entering ${NEW_PHASE}."
  echo
  if bash scripts/check_phase_gate.sh --through "$prev_phase"; then
    GATE_OK=true
  else
    GATE_OK=false
  fi
fi

if ! $GATE_OK; then
  if [[ "${ADVANCE_PHASE_FORCE:-0}" == "1" ]]; then
    echo
    echo "ADVANCE_PHASE_FORCE=1 set — proceeding despite incomplete gate."
    echo "This is logged; the user must accept the risk."
  else
    echo
    echo "REFUSED to advance to $NEW_PHASE — earlier phases are incomplete."
    echo "Route the upstream agents to finish the missing items first."
    echo "If you really need to override (e.g. the user explicitly waived"
    echo "a deliverable), re-run with: ADVANCE_PHASE_FORCE=1 bash scripts/advance_phase.sh $NEW_PHASE"
    exit 1
  fi
fi

# --- Update TASK.md ----------------------------------------------------
if [[ -f TASK.md ]]; then
  # Replace the "- Phase:" line in the "## Current Phase" block.
  awk -v new="$NEW_PHASE" '
    BEGIN { in_section = 0 }
    /^## Current Phase/ { in_section = 1 }
    /^## / && !/^## Current Phase/ { in_section = 0 }
    in_section && /^- Phase:/ { print "- Phase: " new; next }
    in_section && /^- Status:/ { print "- Status: IN_PROGRESS"; next }
    { print }
  ' TASK.md > TASK.md.new
  mv TASK.md.new TASK.md
  echo "Updated TASK.md → Phase: $NEW_PHASE"
fi

# --- Update memory/_PROJECT_STATE.md ----------------------------------
STATE=memory/_PROJECT_STATE.md
if [[ -f "$STATE" ]]; then
  TS="$(date '+%Y-%m-%d %H:%M:%S')"

  # 1) bump "Current phase" — replace EVERYTHING between this heading
  #    and the next "## " heading with a single clean phase line.
  awk -v new="$NEW_PHASE" '
    BEGIN { in_section = 0 }
    /^## Current phase/ {
      print
      print ""
      print new
      print ""
      in_section = 1
      next
    }
    in_section == 1 && /^## / {
      in_section = 0
      print
      next
    }
    in_section == 1 { next }
    { print }
  ' "$STATE" > "$STATE.new"
  mv "$STATE.new" "$STATE"

  # 2) tick the "Phase completion" checkbox for the just-finished phase
  if (( new_idx > 0 )); then
    prev_phase="${PHASES[$(( new_idx - 1 ))]}"
    # macOS-friendly sed
    sed -i.bak "s|- \[ \] ${prev_phase}|- [x] ${prev_phase}|" "$STATE"
    rm -f "$STATE.bak"
  fi

  # 3) append session-log line
  printf "\n- %s — advanced to %s\n" "$TS" "$NEW_PHASE" >> "$STATE"
  echo "Updated memory/_PROJECT_STATE.md (phase + checkbox + session log)"
fi

# --- Append an Orchestrator memory entry ------------------------------
mkdir -p memory
{
  echo
  echo "### $(date '+%Y-%m-%d %H:%M') — advanced to $NEW_PHASE"
  if $GATE_OK; then
    echo "Phase gate ${PHASES[$(( new_idx > 0 ? new_idx - 1 : 0 ))]} passed; team can start $NEW_PHASE work."
  else
    echo "Phase gate did NOT pass but ADVANCE_PHASE_FORCE was used. User accepted the risk."
  fi
} >> memory/ORCHESTRATOR.md

echo
echo "DONE. Project is now at phase: $NEW_PHASE"
