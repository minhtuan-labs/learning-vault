#!/usr/bin/env bash
set -euo pipefail

# v10.3 — A worker pane reports status to the Orchestrator without
# expecting an answer.
#
# Use this for one-way events: "build green", "tests PASS", "app
# deployed at http://localhost:3000". For things that need a reply,
# use ask_orchestrator.sh instead.
#
# Usage:
#   bash scripts/notify_orchestrator.sh <FROM_ROLE> "<one-line message>"
#
# Optional body: pipe extra context into stdin.
#   echo "deployment log" | bash scripts/notify_orchestrator.sh DELIVERY "Deployed"

FROM="${1:-}"
SUBJECT="${2:-}"

if [[ -z "$FROM" || -z "$SUBJECT" ]]; then
  echo "Usage: bash scripts/notify_orchestrator.sh <FROM_ROLE> \"<one-line subject>\""
  echo "Roles: PM SA BA UX BE FE QA DELIVERY"
  exit 1
fi

if [[ "$FROM" == "ORCHESTRATOR" ]]; then
  echo "ORCHESTRATOR does not notify itself."
  exit 1
fi

case "$FROM" in
  PM|SA|BA|UX|BE|FE|QA|DELIVERY) ;;
  *)
    echo "Unknown role: $FROM"
    exit 1
    ;;
esac

mkdir -p .pane_notifications

TS="$(date +%Y%m%d_%H%M%S)"
NID="${FROM}_${TS}"
NOTIF_FILE=".pane_notifications/${NID}.md"

# Read optional body from stdin if anything is piped in.
BODY=""
if [ ! -t 0 ]; then
  BODY="$(cat)"
fi

cat > "$NOTIF_FILE" <<EOF
# Notification — $NID

- From role : $FROM
- At        : $(date '+%Y-%m-%d %H:%M:%S')
- Subject   : $SUBJECT

EOF
if [[ -n "$BODY" ]]; then
  cat >> "$NOTIF_FILE" <<EOF
## Detail

\`\`\`
$BODY
\`\`\`
EOF
fi

NOTIF_LOG=".pane_notifications/_log.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] NOTICE $NID  ($FROM)  $SUBJECT" >> "$NOTIF_LOG"

# v10.4 — Auto-wake Orchestrator (see ask_orchestrator.sh for full
# rationale). Push a one-line [INBOX] event into the TUI and submit.

ORCH_PANE=""
if [[ -f ".agent_panes" ]]; then
  ORCH_PANE="$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2- || true)"
fi

AUTO_PING_ORCHESTRATOR="${AUTO_PING_ORCHESTRATOR:-true}"
if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi

if command -v tmux >/dev/null 2>&1; then
  UNREAD="$(ls -1 .pane_notifications/*.md 2>/dev/null | grep -v _log.log | wc -l | tr -d ' ')"
  tmux set-option status-right "Notif: ${UNREAD} | #(date '+%H:%M %d-%b')" 2>/dev/null || true

  if [[ -n "$ORCH_PANE" && "$AUTO_PING_ORCHESTRATOR" == "true" ]]; then
    # v10.12.1 — broader case to include `claude` engine + bash (waiting
    # for Enter in the auto-relaunch loop). Previously only opencode/node
    # matched → claude sessions silently lost auto-wake.
    PANE_CMD="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo unknown)"
    case "$PANE_CMD" in
      opencode|claude|node|go|main|bash|sh|zsh)
        PING_MSG="[INBOX] new notification from ${FROM}: ${SUBJECT}. Run: bash scripts/list_pending_questions.sh — relay the update to the user."
        tmux send-keys -t "$ORCH_PANE" "$PING_MSG" 2>/dev/null || true
        sleep 0.2
        tmux send-keys -t "$ORCH_PANE" C-m 2>/dev/null || true
        ;;
      *)
        echo "  (skipped auto-wake — Orchestrator pane is running '$PANE_CMD', not a known engine/shell)"
        ;;
    esac
  fi
fi

echo "================================================================"
echo " NOTIFICATION FILED (from $FROM)"
echo "================================================================"
echo " Subject : $SUBJECT"
echo " File    : $NOTIF_FILE"
echo " The Orchestrator will surface this on the next user turn via"
echo "   bash scripts/list_pending_questions.sh"
echo "================================================================"
