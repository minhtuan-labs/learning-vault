#!/usr/bin/env bash
set -euo pipefail

AGENT="${1:-${AGENT_NAME:-UNKNOWN}}"
MODEL="${2:-${AGENT_MODEL:-UNKNOWN}}"
PROJECT="${3:-${PROJECT_NAME:-UNKNOWN}}"

# v10.12 — also surface engine + window
ENGINE_TXT="${ENGINE:-?}"
case "$AGENT" in
  ORCHESTRATOR) WIN="0:OC" ;;
  PM|SA|BA|UX)  WIN="1:DESIGN" ;;
  BE|FE|QA|DELIVERY) WIN="2:DEV" ;;
  *) WIN="?" ;;
esac

line="======================================================================"
echo "$line"
printf " AGENT: %-14s | PROJECT: %-24s\n" "$AGENT" "$PROJECT"
printf " MODEL: %s\n" "$MODEL"
printf " ENGINE: %-10s | WINDOW: %s\n" "$ENGINE_TXT" "$WIN"
echo "$line"
echo " Role prompt : prompts/agents/$AGENT.md"
echo " Instructions: AGENTS.md  (CLAUDE.md is auto-synced for Claude engine)"
echo " Route work  : bash scripts/route_to_pane.sh <AGENT> \"message\""
echo " Phase route : bash scripts/delegate_phase.sh <phase>   (incl. 'release')"
echo " Ask user    : bash scripts/ask_orchestrator.sh <AGENT> \"question\""
echo " Notify user : bash scripts/notify_orchestrator.sh <AGENT> \"event\""
echo " Inbox       : bash scripts/list_pending_questions.sh   (Qs + notifs)"
echo " Answer Q    : bash scripts/answer_role.sh <ROLE> <qid> \"answer\""
echo " Verify      : bash scripts/verify_routing.sh"
echo " Template    : v10.12 (engine choice + 3-window tmux layout)"
echo "$line"

if [[ "$AGENT" == "ORCHESTRATOR" ]]; then
  echo " Tip: $ENGINE_TXT auto-relaunches if it exits. Press Enter to relaunch."
  echo "      Switch tmux window: Ctrl+B 0 (OC) | 1 (DESIGN) | 2 (DEV)"
  echo "$line"
fi
