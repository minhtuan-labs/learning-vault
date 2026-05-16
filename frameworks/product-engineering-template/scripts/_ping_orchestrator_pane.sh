#!/usr/bin/env bash
# v10.15 — Auto-wake helper, shared by ask_orchestrator.sh,
# notify_orchestrator.sh, and watcher_daemon.sh.
#
# Why this exists:
#   - Claude Code's TUI (Ink / React-based) ignores raw tmux send-keys
#     input. It only treats input as a real user message when the input
#     is wrapped in bracketed-paste markers (ESC[200~ ... ESC[201~).
#   - OpenCode's TUI (BubbleTea) accepts bracketed paste correctly too.
#   - When the Orchestrator pane is between engine sessions (in the
#     auto-relaunch `read -r _` shell loop), we first press Enter to
#     trigger the relaunch, wait until the engine is up, then paste.
#
# Usage:
#   bash scripts/_ping_orchestrator_pane.sh "<ping message>"
#
# Exit codes:
#   0   ping delivered (or quietly skipped because no Orchestrator pane)
#   1   usage error
#
# Tunable env:
#   PING_WAIT_AFTER_PASTE  seconds to wait after paste before Enter (default 0.6)
#   PING_BOOT_POLL_MAX     max polls while waiting for engine to come up (default 12 × 0.5s = 6s)

set -u

PING_MSG="${1:-}"
if [[ -z "$PING_MSG" ]]; then
  echo "Usage: bash scripts/_ping_orchestrator_pane.sh \"<message>\"" >&2
  exit 1
fi

ORCH_PANE=""
if [[ -f .agent_panes ]]; then
  ORCH_PANE="$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2- || true)"
fi

if [[ -z "$ORCH_PANE" ]]; then
  exit 0   # no session running — nothing to ping
fi

if ! command -v tmux >/dev/null 2>&1; then
  exit 0
fi

# Disable knob (used by tests / debug runs).
AUTO_PING_ORCHESTRATOR="${AUTO_PING_ORCHESTRATOR:-true}"
if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi
if [[ "$AUTO_PING_ORCHESTRATOR" != "true" ]]; then
  exit 0
fi

PING_WAIT_AFTER_PASTE="${PING_WAIT_AFTER_PASTE:-0.6}"
PING_BOOT_POLL_MAX="${PING_BOOT_POLL_MAX:-12}"

# Bracketed-paste sequence wraps the message. Embed the real ESC (0x1b)
# directly in the string so `tmux send-keys -l` sends it verbatim.
ESC=$'\033'
PASTE_START="${ESC}[200~"
PASTE_END="${ESC}[201~"

paste_and_submit() {
  local pane="$1"
  local msg="$2"
  tmux send-keys -t "$pane" -l "${PASTE_START}${msg}${PASTE_END}" 2>/dev/null || return 1
  sleep "$PING_WAIT_AFTER_PASTE"
  tmux send-keys -t "$pane" Enter 2>/dev/null || return 1
  return 0
}

PANE_CMD="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo unknown)"

case "$PANE_CMD" in
  claude|opencode|node|go|main)
    # Engine TUI is running — paste directly.
    paste_and_submit "$ORCH_PANE" "$PING_MSG" || true
    ;;
  bash|sh|zsh)
    # Pane is in the auto-relaunch shell loop sitting at `read -r _`.
    # Press Enter to wake it; the loop will relaunch the engine.
    tmux send-keys -t "$ORCH_PANE" Enter 2>/dev/null || true
    # Poll until the engine comes back up, then paste the message into it.
    sent=false
    for _ in $(seq 1 "$PING_BOOT_POLL_MAX"); do
      sleep 0.5
      cmd2="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo bash)"
      case "$cmd2" in
        claude|opencode|node|go|main)
          # Extra delay so the engine has finished drawing its prompt
          # before we paste — otherwise some TUIs eat the paste.
          sleep 0.8
          if paste_and_submit "$ORCH_PANE" "$PING_MSG"; then
            sent=true
          fi
          break
          ;;
      esac
    done
    if ! $sent; then
      echo "  (auto-wake: engine did not come up within $((PING_BOOT_POLL_MAX/2))s; falling back to file inbox only)" >&2
    fi
    ;;
  *)
    echo "  (skipped auto-wake — Orchestrator pane is running '$PANE_CMD', not a known engine/shell)" >&2
    ;;
esac

exit 0
