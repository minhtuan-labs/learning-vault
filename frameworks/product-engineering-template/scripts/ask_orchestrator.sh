#!/usr/bin/env bash
set -euo pipefail

# v10.2 — A worker pane files a clarification request for the user.
#
# Usage (called by worker LLM via bash tool):
#   bash scripts/ask_orchestrator.sh <FROM_ROLE> "<question text>"
#
# Behavior:
#   1. Creates .pane_questions/<FROM>_<ts>.md  — the question record.
#   2. Appends to .pane_questions/_pending.log — single audit trail.
#   3. Best-effort notifies the Orchestrator pane via tmux (no Enter
#      is sent, so the user's current input is not submitted).
#   4. Prints a clear hint into the calling pane so anyone glancing at
#      the worker sees "clarification pending".
#
# After calling this, the worker MUST end its current turn and exit.
# The Orchestrator will eventually run scripts/answer_role.sh, which
# re-routes this same role with the user's answer attached.

FROM="${1:-}"
QUESTION="${2:-}"

if [[ -z "$FROM" || -z "$QUESTION" ]]; then
  echo "Usage: bash scripts/ask_orchestrator.sh <FROM_ROLE> \"<question text>\""
  echo "Roles: PM SA BA UX BE FE QA DELIVERY"
  exit 1
fi

if [[ "$FROM" == "ORCHESTRATOR" ]]; then
  echo "ORCHESTRATOR talks to the user directly. Do not call ask_orchestrator.sh from the Orchestrator pane."
  exit 1
fi

case "$FROM" in
  PM|SA|BA|UX|BE|FE|QA|DELIVERY) ;;
  *)
    echo "Unknown role: $FROM"
    echo "Valid roles: PM SA BA UX BE FE QA DELIVERY"
    exit 1
    ;;
esac

mkdir -p .pane_questions

TS="$(date +%Y%m%d_%H%M%S)"
QID="${FROM}_${TS}"
QUESTION_FILE=".pane_questions/${QID}.md"

# Find the most recent task file for this role (if any) so the answerer
# can reconstruct context.
LAST_TASK="$(ls -t .pane_tasks/${FROM}_*.md 2>/dev/null | head -n1 || true)"

cat > "$QUESTION_FILE" <<EOF
# Clarification request — $QID

- From role     : $FROM
- Created at    : $(date '+%Y-%m-%d %H:%M:%S')
- Status        : pending
- Related task  : ${LAST_TASK:-(none recorded)}

## Question for the user

$QUESTION

## How the Orchestrator should resolve this

1. Read the question above. If anything is unclear, ask the user a
   focused follow-up — do not guess on behalf of $FROM.
2. Once the user gives an answer, run:

   \`\`\`bash
   bash scripts/answer_role.sh $FROM $QID "<user's answer>"
   \`\`\`

3. \`answer_role.sh\` writes the answer to \`.pane_answers/${QID}.md\`
   and automatically routes $FROM with the answer attached, so $FROM
   can resume the previous task.
EOF

# Append a single pending-log line so list_pending_questions.sh stays fast.
PENDING_LOG=".pane_questions/_pending.log"
SHORT_Q="${QUESTION:0:120}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PENDING  $QID  ($FROM)  Q: ${SHORT_Q}" >> "$PENDING_LOG"

# v10.4 — Auto-wake the Orchestrator.
#
# When a worker files a question, we now actively push a one-line
# [INBOX] message into the Orchestrator's TUI input and press Enter,
# so OpenCode (the Orchestrator) starts processing immediately rather
# than sitting idle waiting for the user to ask "any pending?".
#
# Risks: if the user was mid-typing, the inbox notice gets appended to
# their input before submission. The Orchestrator prompt is instructed
# to handle compound messages (run list_pending_questions.sh first,
# then address whatever else the user said). Set
# AUTO_PING_ORCHESTRATOR=false in config/opencode.env to disable.

ORCH_PANE=""
if [[ -f ".agent_panes" ]]; then
  ORCH_PANE="$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2- || true)"
fi

AUTO_PING_ORCHESTRATOR="${AUTO_PING_ORCHESTRATOR:-true}"
if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi

if [[ -n "$ORCH_PANE" ]] && command -v tmux >/dev/null 2>&1; then
  # Update tmux status-right so the user has a passive count, too.
  PENDING_COUNT="$(grep -c '^\[.*\] PENDING ' "$PENDING_LOG" 2>/dev/null || echo 0)"
  ANSWERED_COUNT="$(grep -c '^\[.*\] ANSWERED ' "$PENDING_LOG" 2>/dev/null || echo 0)"
  OPEN=$((PENDING_COUNT - ANSWERED_COUNT))
  if (( OPEN < 0 )); then OPEN=0; fi
  tmux set-option status-right "Pending Q: ${OPEN} | #(date '+%H:%M %d-%b')" 2>/dev/null || true

  if [[ "$AUTO_PING_ORCHESTRATOR" == "true" ]]; then
    # Only auto-ping if the Orchestrator pane appears to be running
    # opencode (TUI). If it's at bash, the keystrokes would become a
    # botched command — skip and rely on the next user turn to surface.
    PANE_CMD="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo unknown)"
    if [[ "$PANE_CMD" =~ ^(opencode|node|go|main)$ ]] || [[ "$PANE_CMD" == "opencode" ]]; then
      PING_MSG="[INBOX] new clarification from ${FROM} (id: ${QID}). Run: bash scripts/list_pending_questions.sh — read the question to me and ask the user for an answer."
      tmux send-keys -t "$ORCH_PANE" "$PING_MSG" 2>/dev/null || true
      sleep 0.2
      tmux send-keys -t "$ORCH_PANE" C-m 2>/dev/null || true
    fi
  fi
fi

echo "================================================================"
echo " CLARIFICATION PENDING (from $FROM)"
echo "================================================================"
echo " Question id : $QID"
echo " File        : $QUESTION_FILE"
echo " Related task: ${LAST_TASK:-(none)}"
echo
echo " The Orchestrator will resume $FROM with the user's answer by"
echo " running: bash scripts/answer_role.sh $FROM $QID \"<answer>\""
echo
echo " $FROM should stop work now and exit the current OpenCode turn."
echo "================================================================"
