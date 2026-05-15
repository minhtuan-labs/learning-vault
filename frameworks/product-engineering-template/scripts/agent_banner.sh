#!/usr/bin/env bash
set -euo pipefail

AGENT="${1:-${AGENT_NAME:-UNKNOWN}}"
MODEL="${2:-${AGENT_MODEL:-UNKNOWN}}"
PROJECT="${3:-${PROJECT_NAME:-UNKNOWN}}"

line="======================================================================"
echo "$line"
printf " AGENT: %-14s | PROJECT: %-24s\n" "$AGENT" "$PROJECT"
printf " MODEL: %s\n" "$MODEL"
echo "$line"
echo " Role prompt : prompts/agents/$AGENT.md"
echo " Instructions: AGENTS.md (auto-loaded by OpenCode at startup)"
echo " Route work  : bash scripts/route_to_pane.sh <AGENT> \"message\""
echo " Phase route : bash scripts/delegate_phase.sh <phase>   (incl. 'release')"
echo " Ask user    : bash scripts/ask_orchestrator.sh <AGENT> \"question\""
echo " Notify user : bash scripts/notify_orchestrator.sh <AGENT> \"event\""
echo " Inbox       : bash scripts/list_pending_questions.sh   (Qs + notifs)"
echo " Answer Q    : bash scripts/answer_role.sh <ROLE> <qid> \"answer\""
echo " Verify      : bash scripts/verify_routing.sh"
echo " Template    : v10.11 (framework files immutable + safe sync script)"
echo "$line"

if [[ "$AGENT" == "ORCHESTRATOR" ]]; then
  echo " Tip: OpenCode auto-relaunches if it exits. If you see a"
  echo "      '[v10.2] opencode exited' prompt, just press Enter to relaunch."
  echo "      To stay at shell, press Ctrl+C or Ctrl+D at that prompt."
  echo "$line"
fi
