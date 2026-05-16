#!/usr/bin/env bash
set -euo pipefail

# v10.2 — Orchestrator records the user's answer to a clarification
# request and re-routes the originating role with the answer in hand.
#
# Usage (called by Orchestrator LLM via bash tool):
#   bash scripts/answer_role.sh <TO_ROLE> <question_id> "<user's answer>"
#
# Example:
#   bash scripts/answer_role.sh SA SA_20260514_080000 "Use Postgres."

TO="${1:-}"
QID="${2:-}"
ANSWER="${3:-}"

if [[ -z "$TO" || -z "$QID" || -z "$ANSWER" ]]; then
  echo "Usage: bash scripts/answer_role.sh <TO_ROLE> <question_id> \"<answer text>\""
  echo "Roles: PM SA BA UX BE FE QA DELIVERY"
  echo
  echo "To see question ids:  bash scripts/list_pending_questions.sh"
  exit 1
fi

case "$TO" in
  PM|SA|BA|UX|BE|FE|QA|DELIVERY) ;;
  *)
    echo "Unknown role: $TO"
    exit 1
    ;;
esac

QUESTION_FILE=".pane_questions/${QID}.md"
ANSWER_FILE=".pane_answers/${QID}.md"

if [[ ! -f "$QUESTION_FILE" ]]; then
  echo "WARNING: question file $QUESTION_FILE not found. Continuing anyway."
fi

if [[ -f "$ANSWER_FILE" ]]; then
  echo "NOTE: $ANSWER_FILE already exists — overwriting with the new answer."
fi

mkdir -p .pane_answers

cat > "$ANSWER_FILE" <<EOF
# Answer for $QID

- For role    : $TO
- Answered at : $(date '+%Y-%m-%d %H:%M:%S')
- Source      : user (relayed through Orchestrator)

## Original question

$(cat "$QUESTION_FILE" 2>/dev/null || echo "(question file missing)")

## Answer

$ANSWER
EOF

# Mark the question as answered in the pending log.
PENDING_LOG=".pane_questions/_pending.log"
mkdir -p .pane_questions
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ANSWERED $QID  ($TO)  A: ${ANSWER:0:120}" >> "$PENDING_LOG"

# Update tmux status with the new open-question count if possible.
if command -v tmux >/dev/null 2>&1; then
  PENDING_COUNT="$(grep -c '^\[.*\] PENDING ' "$PENDING_LOG" 2>/dev/null || echo 0)"
  ANSWERED_COUNT="$(grep -c '^\[.*\] ANSWERED ' "$PENDING_LOG" 2>/dev/null || echo 0)"
  OPEN=$((PENDING_COUNT - ANSWERED_COUNT))
  if (( OPEN < 0 )); then OPEN=0; fi
  if (( OPEN > 0 )); then
    tmux set-option status-right "Pending Q: ${OPEN} | #(date '+%H:%M %d-%b')" 2>/dev/null || true
  else
    tmux set-option status-right "#(date '+%H:%M %d-%b')" 2>/dev/null || true
  fi
fi

echo "Answer saved: $ANSWER_FILE"
echo "Now resuming $TO with the answer attached..."
echo

# Compose a resume message and route it. route_to_pane.sh writes a fresh
# .pane_tasks/<TO>_<ts>.md and spawns opencode run --model <TO_MODEL>.
RESUME_MSG="Resume your previous task in this pane. The user has answered the clarification you filed earlier (question id: $QID). Steps: (1) read memory/_PROJECT_STATE.md and memory/$TO.md for continuity, (2) re-read prompts/agents/$TO.md, (3) find the most recent task file in .pane_tasks/${TO}_*.md (the one filed BEFORE you called ask_orchestrator.sh), (4) read the answer in $ANSWER_FILE, (5) continue the work you paused, applying the user's decision. Do not re-ask the same question. Before you exit, append a dated entry to memory/$TO.md describing the decision now that you have the answer. If you need a different clarification later, call bash scripts/ask_orchestrator.sh $TO \"<new question>\" again."

bash scripts/route_to_pane.sh "$TO" "$RESUME_MSG"

echo
echo "Done. $TO is resuming with the answer at $ANSWER_FILE."
