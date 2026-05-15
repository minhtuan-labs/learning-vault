#!/usr/bin/env bash
set -euo pipefail

# v10 — Run a routed task file in the current shell (used by tooling/tests).
# Same v10 fix as route_to_pane.sh: real .opencode/config.json + --config flag.

ROLE="${1:-}"
TASK_FILE="${2:-}"

if [[ -z "$ROLE" || -z "$TASK_FILE" ]]; then
  echo "Usage: bash scripts/run_agent_task.sh <PANE_ROLE> <task_file>"
  exit 1
fi

if [[ ! -f "$TASK_FILE" ]]; then
  echo "Task file not found: $TASK_FILE"
  exit 1
fi

source config/agent_models.env

MODEL_VAR="${ROLE}_MODEL"
MODEL="${!MODEL_VAR:-}"

if [[ -z "$MODEL" ]]; then
  echo "No model configured for $ROLE"
  exit 1
fi

OPENCODE_CONFIG_PATH="$(pwd)/.opencode/config.json"
if [[ ! -f "$OPENCODE_CONFIG_PATH" ]]; then
  echo "Missing $OPENCODE_CONFIG_PATH"
  echo "Run scripts/start_agents_tmux.sh first; it regenerates the config."
  exit 1
fi

OPENCODE_CONFIG="$OPENCODE_CONFIG_PATH" opencode run \
  --model "$MODEL" \
  "Execute the routed pane task described in $TASK_FILE. Read the file, perform the work, update files as needed, and report completion. Do not use internal subagents (task tool is disabled in .opencode/config.json and AGENTS.md)."
