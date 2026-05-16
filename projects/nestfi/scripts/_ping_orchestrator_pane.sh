#!/usr/bin/env bash
# v10.18.1 — Auto-wake helper. Fix: permissive pane_current_command match.
# Claude Code shows up as its version string ("2.1.143") not "claude" on
# some macOS setups, so the v10.18 case statement silently skipped all
# delivery methods. Now any non-shell, non-empty command is treated as
# an engine TUI.
#
# Why this is complex:
#   Claude Code's Ink TUI (Node + readline raw mode) doesn't reliably
#   pick up tmux send-keys / paste-buffer injections. OpenCode's
#   BubbleTea TUI does. v10.15 (manual ESC bracketed-paste) and v10.17
#   (paste-buffer -p) both failed on Claude in practice.
#
# Strategy:
#   Try multiple delivery methods, verify each by reading the pane
#   buffer afterwards. As soon as the ping text appears in the pane
#   buffer, send Enter. If no method delivers, fall back to a visible
#   user nudge: red status-right + macOS notification + tmux bell.
#
# Methods tried (in order):
#   1. tmux load-buffer + paste-buffer -p  (bracketed paste, fast)
#   2. tmux send-keys -l "$msg"             (literal characters, fast)
#   3. char-by-char typewriter mode         (mimic real typing, slow but reliable)
#
# Every attempt is logged to .pane_logs/_auto_wake.log with method,
# pane state, and outcome.
#
# Usage:
#   bash scripts/_ping_orchestrator_pane.sh "<ping message>"
#
# Tunable env:
#   PING_WAIT_AFTER_PASTE  seconds after paste before Enter (default 0.8)
#   PING_BOOT_POLL_MAX     polls while waiting for engine boot (default 12 × 0.5s)
#   PING_VERIFY_TIMEOUT    seconds to wait for ping text to appear (default 1.5)
#   PING_TYPEWRITER_DELAY  seconds between chars in typewriter mode (default 0.04)
#   AUTO_PING_ORCHESTRATOR set to "false" to disable auto-wake
#   AUTO_WAKE_USE_OSASCRIPT set to "false" to disable macOS notification

set -u

PING_MSG="${1:-}"
if [[ -z "$PING_MSG" ]]; then
  echo "Usage: bash scripts/_ping_orchestrator_pane.sh \"<message>\"" >&2
  exit 1
fi

mkdir -p .pane_logs
LOG=".pane_logs/_auto_wake.log"

log_ping() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

ORCH_PANE=""
if [[ -f .agent_panes ]]; then
  ORCH_PANE="$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2- || true)"
fi

if [[ -z "$ORCH_PANE" ]]; then
  log_ping "SKIP — no .agent_panes / no Orchestrator pane registered"
  exit 0
fi

if ! command -v tmux >/dev/null 2>&1; then
  log_ping "SKIP — tmux not in PATH"
  exit 0
fi

AUTO_PING_ORCHESTRATOR="${AUTO_PING_ORCHESTRATOR:-true}"
if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi
if [[ "$AUTO_PING_ORCHESTRATOR" != "true" ]]; then
  log_ping "SKIP — AUTO_PING_ORCHESTRATOR=false"
  exit 0
fi

PING_WAIT_AFTER_PASTE="${PING_WAIT_AFTER_PASTE:-0.8}"
PING_BOOT_POLL_MAX="${PING_BOOT_POLL_MAX:-12}"
PING_VERIFY_TIMEOUT="${PING_VERIFY_TIMEOUT:-1.5}"
PING_TYPEWRITER_DELAY="${PING_TYPEWRITER_DELAY:-0.04}"
AUTO_WAKE_USE_OSASCRIPT="${AUTO_WAKE_USE_OSASCRIPT:-true}"

# Verification: does the pane buffer contain a sentinel substring of the ping?
# We use the first 30 chars of the ping body (skip the [INBOX] prefix to
# avoid false positives from older pings still on screen).
#
# Uses awk for float→int conversion (portable; bc not assumed installed).
verify_delivered() {
  local pane="$1"
  local needle="$2"
  local timeout="$3"
  local timeout_ds
  timeout_ds=$(awk -v t="$timeout" 'BEGIN { printf "%d", t * 10 }')
  local elapsed_ds=0
  while (( elapsed_ds < timeout_ds )); do
    if tmux capture-pane -p -t "$pane" 2>/dev/null | grep -Fq "$needle"; then
      return 0
    fi
    sleep 0.3
    elapsed_ds=$((elapsed_ds + 3))
  done
  return 1
}

# Method 1: tmux load-buffer + paste-buffer -p (bracketed paste).
method_paste_buffer() {
  local pane="$1"
  local msg="$2"
  printf '%s' "$msg" | tmux load-buffer - 2>/dev/null || return 1
  tmux paste-buffer -p -t "$pane" 2>/dev/null || \
    tmux paste-buffer -t "$pane" 2>/dev/null || return 1
  return 0
}

# Method 2: tmux send-keys -l with full literal string (no bracketed paste).
method_send_keys_literal() {
  local pane="$1"
  local msg="$2"
  tmux send-keys -t "$pane" -l "$msg" 2>/dev/null
}

# Method 3: char-by-char typewriter, mimics a human typing slowly.
method_typewriter() {
  local pane="$1"
  local msg="$2"
  local i
  for ((i = 0; i < ${#msg}; i++)); do
    tmux send-keys -t "$pane" -l "${msg:$i:1}" 2>/dev/null
    sleep "$PING_TYPEWRITER_DELAY"
  done
}

submit_enter() {
  local pane="$1"
  sleep "$PING_WAIT_AFTER_PASTE"
  tmux send-keys -t "$pane" Enter 2>/dev/null
  # Extra Enter in case the first was eaten by Claude's input filter.
  sleep 0.3
  tmux send-keys -t "$pane" Enter 2>/dev/null
}

# Visible fallback when no delivery method worked.
fire_visible_alert() {
  local count="$1"
  # tmux bell
  tmux display-message -t "$ORCH_PANE" "Orchestrator inbox: $count pending" 2>/dev/null || true
  # macOS notification
  if [[ "$AUTO_WAKE_USE_OSASCRIPT" == "true" ]] && [[ "$(uname -s)" == "Darwin" ]] \
      && command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$count pending — auto-wake failed, please nudge Orchestrator (Prefix+W)\" with title \"Orchestrator inbox\" sound name \"Glass\"" 2>/dev/null || true
  fi
}

PANE_CMD="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo unknown)"
log_ping "FIRE pane=$ORCH_PANE running=$PANE_CMD msglen=${#PING_MSG}"

# A short, distinctive sentinel from the message body — first 30 chars
# after any [INBOX] prefix.
SENTINEL="${PING_MSG#\[INBOX\] }"
SENTINEL="${SENTINEL:0:30}"

try_deliver_to_tui() {
  local pane="$1"
  local msg="$2"

  # Method 1
  if method_paste_buffer "$pane" "$msg"; then
    submit_enter "$pane"
    if verify_delivered "$pane" "$SENTINEL" "$PING_VERIFY_TIMEOUT"; then
      log_ping "SENT via paste-buffer to pane=$pane"
      return 0
    fi
    log_ping "RETRY — paste-buffer not verified in pane=$pane"
  fi

  # Method 2
  if method_send_keys_literal "$pane" "$msg"; then
    submit_enter "$pane"
    if verify_delivered "$pane" "$SENTINEL" "$PING_VERIFY_TIMEOUT"; then
      log_ping "SENT via send-keys-literal to pane=$pane"
      return 0
    fi
    log_ping "RETRY — send-keys-literal not verified in pane=$pane"
  fi

  # Method 3 — slow path. Skip if message is huge (would take too long).
  if (( ${#msg} <= 400 )); then
    method_typewriter "$pane" "$msg"
    submit_enter "$pane"
    if verify_delivered "$pane" "$SENTINEL" "$PING_VERIFY_TIMEOUT"; then
      log_ping "SENT via typewriter to pane=$pane"
      return 0
    fi
    log_ping "RETRY — typewriter not verified in pane=$pane"
  else
    log_ping "SKIP — typewriter (msg too long: ${#msg} chars > 400)"
  fi

  return 1
}

case "$PANE_CMD" in
  claude|opencode|node|go|main|python|python3|ruby|java|deno|bun)
    if try_deliver_to_tui "$ORCH_PANE" "$PING_MSG"; then
      :
    else
      PENDING="$(ls -1 .pane_questions/*.md .pane_notifications/*.md 2>/dev/null \
                  | grep -v _log.log | wc -l | tr -d ' ')"
      log_ping "FAIL — all methods failed; pending=$PENDING. Firing visible alert."
      fire_visible_alert "$PENDING"
    fi
    ;;
  bash|sh|zsh|fish|tcsh|ksh|dash)
    log_ping "WAKE — shell loop, sending Enter to relaunch then polling"
    tmux send-keys -t "$ORCH_PANE" Enter 2>/dev/null || true
    sent=false
    for _ in $(seq 1 "$PING_BOOT_POLL_MAX"); do
      sleep 0.5
      cmd2="$(tmux display-message -p -t "$ORCH_PANE" '#{pane_current_command}' 2>/dev/null || echo bash)"
      case "$cmd2" in
        bash|sh|zsh|fish|tcsh|ksh|dash) continue ;;
        ""|unknown) continue ;;
        *)
          sleep 0.8
          if try_deliver_to_tui "$ORCH_PANE" "$PING_MSG"; then
            sent=true
          fi
          break
          ;;
      esac
    done
    if ! $sent; then
      PENDING="$(ls -1 .pane_questions/*.md .pane_notifications/*.md 2>/dev/null \
                  | grep -v _log.log | wc -l | tr -d ' ')"
      log_ping "TIMEOUT — engine did not come up; pending=$PENDING. Firing visible alert."
      fire_visible_alert "$PENDING"
    fi
    ;;
  ""|unknown)
    log_ping "SKIP — pane_current_command is empty/unknown (genuinely no info)"
    ;;
  *)
    # v10.18.1 — Claude Code shows up as its version string (e.g. "2.1.143")
    # in pane_current_command on some macOS setups. Treat ANY non-shell,
    # non-empty command as a probable engine TUI and try delivery.
    log_ping "ASSUMING engine TUI (pane_current_command='$PANE_CMD' — not on known-shell list)"
    if try_deliver_to_tui "$ORCH_PANE" "$PING_MSG"; then
      :
    else
      PENDING="$(ls -1 .pane_questions/*.md .pane_notifications/*.md 2>/dev/null \
                  | grep -v _log.log | wc -l | tr -d ' ')"
      log_ping "FAIL — all methods failed for '$PANE_CMD'; pending=$PENDING. Firing visible alert."
      fire_visible_alert "$PENDING"
    fi
    ;;
esac

exit 0
