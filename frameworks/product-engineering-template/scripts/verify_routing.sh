#!/usr/bin/env bash
set -euo pipefail

# v10 — Verify that routing actually fired.
#
# Orchestrator (or user) can call this after a delegate_phase / route_to_pane
# to confirm a real bash command ran instead of just being described in chat.
#
# A "real" routing event leaves three artifacts:
#   1) A task file under .pane_tasks/
#   2) A receipt line under .pane_logs/_routing_receipts.log
#   3) A log file under .pane_logs/ (filled as the target pane streams output)

RECEIPT=".pane_logs/_routing_receipts.log"

echo "================================================================"
echo " v10 routing verification"
echo "================================================================"

if [[ ! -d ".pane_tasks" ]]; then
  echo "NO .pane_tasks/ directory yet — no routing has ever fired in this project."
  exit 2
fi

LAST_TASK="$(ls -t .pane_tasks 2>/dev/null | head -n1 || true)"
if [[ -z "$LAST_TASK" ]]; then
  echo "Empty .pane_tasks/ — no routing has fired."
  exit 2
fi

mtime_of() {
  # macOS BSD stat first, then GNU stat (Linux) as fallback.
  if stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$1" >/dev/null 2>&1; then
    stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$1"
  else
    stat -c '%y' "$1" 2>/dev/null | cut -d. -f1
  fi
}

echo "Last task file : .pane_tasks/$LAST_TASK"
echo "  size         : $(wc -c < ".pane_tasks/$LAST_TASK") bytes"
echo "  mtime        : $(mtime_of ".pane_tasks/$LAST_TASK")"

echo
if [[ -f "$RECEIPT" ]]; then
  echo "Last 5 routing receipts:"
  tail -n 20 "$RECEIPT" | sed 's/^/  /'
else
  echo "No routing receipts file at $RECEIPT — routing scripts have not been called."
fi

echo
LAST_LOG="$(ls -t .pane_logs 2>/dev/null | grep -v '_routing_receipts.log' | head -n1 || true)"
if [[ -n "$LAST_LOG" ]]; then
  echo "Last log file  : .pane_logs/$LAST_LOG"
  echo "  size         : $(wc -c < ".pane_logs/$LAST_LOG") bytes"
  echo "  last 10 lines:"
  tail -n 10 ".pane_logs/$LAST_LOG" 2>/dev/null | sed 's/^/    /'
else
  echo "No pane log files yet."
fi

echo
echo "If the Orchestrator told you it routed work but this script shows"
echo "no recent receipt / task / log, then Orchestrator only DESCRIBED"
echo "routing in chat — it did not actually run the bash command."
