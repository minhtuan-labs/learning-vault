#!/usr/bin/env bash
set -euo pipefail

# v10.1 — Manually inject a role's boot prompt into its tmux pane.
#
# Use this AFTER you've confirmed the OpenCode TUI is loaded in that pane.
# v10 stopped doing this automatically because the auto-paste raced with
# opencode startup and could leave the pane stuck at  dquote>  in bash.
#
# Usage:
#   bash scripts/inject_boot_prompt.sh ORCHESTRATOR
#   bash scripts/inject_boot_prompt.sh PM
#
# In practice you usually do NOT need this — AGENTS.md is auto-loaded by
# OpenCode and contains the same instructions. Use this script only when
# AGENTS.md was not picked up (e.g. opencode-go fork that ignores it).

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: bash scripts/inject_boot_prompt.sh <PANE_ROLE>"
  echo "Roles: ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY"
  exit 1
fi

if [[ ! -f ".agent_panes" ]]; then
  echo "Missing .agent_panes. Run scripts/start_agents_tmux.sh first."
  exit 1
fi

PANE_ID="$(grep "^${TARGET}=" .agent_panes | cut -d= -f2- || true)"
if [[ -z "$PANE_ID" ]]; then
  echo "Unknown pane role: $TARGET"
  cut -d= -f1 .agent_panes
  exit 1
fi

BOOT_FILE=".agent_boot_prompts/${TARGET}.txt"
if [[ ! -f "$BOOT_FILE" ]]; then
  echo "Missing $BOOT_FILE (regenerate with scripts/start_agents_tmux.sh)."
  exit 1
fi

echo "[v10.1] Pasting $BOOT_FILE into pane $PANE_ID ($TARGET) ..."
echo "        Make sure the OpenCode TUI is loaded in that pane first."
sleep 1

BUF_NAME="bootprompt_${TARGET}_$$"
tmux load-buffer -b "$BUF_NAME" "$BOOT_FILE"
tmux paste-buffer -b "$BUF_NAME" -t "$PANE_ID"
tmux send-keys -t "$PANE_ID" C-m
tmux delete-buffer -b "$BUF_NAME" 2>/dev/null || true

echo "[v10.1] Done. If the pane was at bash (not the OpenCode TUI), the"
echo "        paste may have produced a partial command — press Ctrl+C in"
echo "        that pane, then start OpenCode with:  opencode --model <model>"
