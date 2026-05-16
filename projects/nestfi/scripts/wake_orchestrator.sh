#!/usr/bin/env bash
set -euo pipefail

# v10.18 — Manual Orchestrator wake.
#
# When auto-wake fails (especially on Claude), this is the fallback:
# types a single "." + Enter into the Orchestrator pane. The "." is
# treated as a user turn, which forces the Orchestrator to run
# list_pending_questions.sh + list_pending_watches.sh per the
# mandatory turn-start rule in prompts/agents/ORCHESTRATOR.md.
#
# Usage:
#   bash scripts/wake_orchestrator.sh
#
# Recommended tmux binding (installed by start_agents_tmux.sh):
#   prefix + W   → bash scripts/wake_orchestrator.sh

if [[ ! -f .agent_panes ]]; then
  echo "No active session (.agent_panes missing). Start a session first."
  exit 1
fi

ORCH_PANE="$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2- || true)"
if [[ -z "$ORCH_PANE" ]]; then
  echo "No ORCHESTRATOR pane registered."
  exit 1
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not in PATH."
  exit 1
fi

tmux send-keys -t "$ORCH_PANE" "." 2>/dev/null || true
sleep 0.2
tmux send-keys -t "$ORCH_PANE" Enter 2>/dev/null || true

echo "Wake nudge sent to Orchestrator pane ($ORCH_PANE)."
