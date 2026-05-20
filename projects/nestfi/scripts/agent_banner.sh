#!/usr/bin/env bash
set -euo pipefail

AGENT="${1:-${AGENT_NAME:-UNKNOWN}}"
MODEL="${2:-${AGENT_MODEL:-UNKNOWN}}"
PROJECT="${3:-${PROJECT_NAME:-UNKNOWN}}"

# v10.21 — friendly display names for the PaneC team.
# Internal identifier (AGENT_NAME) stays uppercase forever; this is
# purely cosmetic for the banner + conversation.
case "$AGENT" in
  ORCHESTRATOR) DISPLAY="Orches" ;;
  DELIVERY)     DISPLAY="Deli" ;;
  *)            DISPLAY="$AGENT" ;;
esac

# v10.16 — also surface engine + window + free-mode flag
ENGINE_TXT="${ENGINE:-?}"
FREE_TXT=""
if [[ "${FREE_MODE:-false}" == "true" ]]; then
  FREE_TXT=" (--free)"
fi
case "$AGENT" in
  ORCHESTRATOR) WIN="0:OC" ;;
  PM|SA|BA|UX)  WIN="1:DESIGN" ;;
  BE|FE|QA|DELIVERY) WIN="2:DEV" ;;
  *) WIN="?" ;;
esac

line="======================================================================"
echo "$line"
printf " AGENT: %-14s | DISPLAY: %-8s | PROJECT: %-20s\n" "$AGENT" "$DISPLAY" "$PROJECT"
printf " TEAM:  PaneC (9-pane crew) \n"
printf " MODEL: %s\n" "$MODEL"
printf " ENGINE: %-10s%-9s | WINDOW: %s\n" "$ENGINE_TXT" "$FREE_TXT" "$WIN"
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
echo " Template    : v10.21 (PaneC team identity + Orches/Deli display names)"
echo " Wake log    : .pane_logs/_auto_wake.log     (tail to audit auto-wake)"
echo " Manual wake : Prefix+W  OR  bash scripts/wake_orchestrator.sh"
echo "$line"

if [[ "$AGENT" == "ORCHESTRATOR" ]]; then
  echo " Tip: $ENGINE_TXT auto-relaunches if it exits. Press Enter to relaunch."
  echo "      Switch tmux window: Ctrl+B 0 (OC) | 1 (DESIGN) | 2 (DEV)"
  echo "$line"
fi
