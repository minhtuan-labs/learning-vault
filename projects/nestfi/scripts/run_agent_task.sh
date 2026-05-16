#!/usr/bin/env bash
set -euo pipefail

# v10.12 — Run a routed task file in the current shell (engine-aware).
# Same v10 fix as route_to_pane.sh: real engine config + correct CLI.

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

# v10.12 — read engine choice from .agent_session, source engine config
ENGINE="opencode"
if [[ -f ".agent_session" ]]; then
  # shellcheck disable=SC1090
  source .agent_session
fi
ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "Missing engine config: $ENGINE_CFG"
  exit 1
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

# v10.16 — apply --free overlay if active.
if [[ "${FREE_MODE:-false}" == "true" ]]; then
  FREE_CFG="config/engines/${ENGINE}-free.env"
  if [[ -f "$FREE_CFG" ]]; then
    # shellcheck disable=SC1090
    source "$FREE_CFG"
  fi
fi

MODEL_VAR="${ROLE}_MODEL"
MODEL="${!MODEL_VAR:-}"

if [[ -z "$MODEL" ]]; then
  echo "No model configured for $ROLE in engine $ENGINE"
  exit 1
fi

ENGINE_CONFIG_ABS="$(pwd)/${ENGINE_CONFIG_PATH}"
if [[ ! -f "$ENGINE_CONFIG_ABS" ]]; then
  echo "Missing $ENGINE_CONFIG_ABS"
  echo "Run scripts/start_agents_tmux.sh first; it regenerates the config."
  exit 1
fi

if [[ -n "$ENGINE_CONFIG_ENV_VAR" ]]; then
  export "${ENGINE_CONFIG_ENV_VAR}=${ENGINE_CONFIG_ABS}"
fi

$ENGINE_RUN_BASE $ENGINE_MODEL_FLAG "$MODEL" \
  "Execute the routed pane task described in $TASK_FILE. Read the file, perform the work, update files as needed, and report completion. Do not use internal subagents (task tool is disabled in $ENGINE_CONFIG_PATH and AGENTS.md)."
