#!/usr/bin/env bash
set -euo pipefail

# v10.12 — Start the 9-pane tmux session with engine choice + 3-window layout.
#
# Usage:
#   bash scripts/start_agents_tmux.sh <project_name> [--engine opencode|claude]
#
# Window layout:
#   Window 0 — OC      : 1 pane  (ORCHESTRATOR — full)
#   Window 1 — DESIGN  : 4 panes (PM, SA, BA, UX) in 2×2 tiled
#   Window 2 — DEV     : 4 panes (BE, FE, QA, DELIVERY) in 2×2 tiled
#
# Engine selection (v10.12, additive):
#   --engine opencode  (default) — opencode-go fork, multi-provider, 7-tier mix
#   --engine claude               — Anthropic Claude Code, 3-tier
#   See config/engines/*.env + config/engines/README.md.

# ---------- arg parsing ----------
INPUT_PROJECT_NAME=""
ENGINE="opencode"          # default

while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine)
      ENGINE="$2"; shift 2 ;;
    --engine=*)
      ENGINE="${1#--engine=}"; shift ;;
    -h|--help)
      echo "Usage: bash scripts/start_agents_tmux.sh <project_name> [--engine opencode|claude]"
      exit 0 ;;
    *)
      if [[ -z "$INPUT_PROJECT_NAME" ]]; then
        INPUT_PROJECT_NAME="$1"
      fi
      shift ;;
  esac
done

CURRENT_FOLDER_NAME="$(basename "$(pwd)")"
if [[ -n "$INPUT_PROJECT_NAME" ]]; then
  SESSION_NAME="$INPUT_PROJECT_NAME"
else
  SESSION_NAME="$CURRENT_FOLDER_NAME"
fi

if [[ ! "$SESSION_NAME" =~ ^[A-Za-z0-9_.-]+$ ]]; then
  echo "Invalid project/session name: $SESSION_NAME"
  echo "Use only letters, numbers, underscore, dash, or dot."
  exit 1
fi

PROJECT_DIR="$(pwd)"

# ---------- engine config ----------
ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "ERROR: engine config not found: $ENGINE_CFG"
  echo "Available engines:"
  ls -1 config/engines/*.env 2>/dev/null | sed 's|config/engines/||;s|.env$||' | sed 's/^/  - /'
  exit 2
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

# Backward-compat: still source the old opencode.env runtime flags if present.
if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi

AGENTS=(ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY)

AUTO_START_ORCHESTRATOR="${AUTO_START_ORCHESTRATOR:-true}"
AUTO_START_WORKER_AGENTS="${AUTO_START_WORKER_AGENTS:-false}"
STRICT_MODEL_CHECK="${STRICT_MODEL_CHECK:-true}"
OPENCODE_EXTRA_ARGS="${OPENCODE_EXTRA_ARGS:-}"
SHOW_AGENT_BANNER="${SHOW_AGENT_BANNER:-true}"

get_agent_model() {
  local agent="$1"
  local var_name="${agent}_MODEL"
  echo "${!var_name:-not_configured}"
}

# ---------- existing-session check ----------
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Session '$SESSION_NAME' already exists."
  echo "Attach with: tmux attach -t '$SESSION_NAME'"
  exit 0
fi

# ---------- model validation ----------
if [[ "$STRICT_MODEL_CHECK" == "true" ]]; then
  if ! command -v "$ENGINE_BINARY" >/dev/null 2>&1; then
    echo "ERROR: engine binary '$ENGINE_BINARY' not found in PATH."
    echo "Install $ENGINE_BINARY, or set STRICT_MODEL_CHECK=false in config/opencode.env."
    exit 1
  fi

  # v10.12 — Claude Code auth-mode warning (avoid accidentally burning API
  # billing when the user has a Pro/Max subscription).
  if [[ "$ENGINE" == "claude" ]] && [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo ""
    echo "============================================================"
    echo "  ⚠  WARNING: ANTHROPIC_API_KEY is set in your environment."
    echo "============================================================"
    echo "  Claude Code will use the **Anthropic API** (billed per"
    echo "  token), NOT your Claude Pro / Max subscription."
    echo ""
    echo "  Multi-agent workflows on Opus/Sonnet can rack up real \$\$\$"
    echo "  on the API. If you have a Pro/Max plan, switch by:"
    echo ""
    echo "    1) For THIS session only:"
    echo "         unset ANTHROPIC_API_KEY    # in this shell, then re-run"
    echo ""
    echo "    2) Permanent (recommended if you have Pro/Max):"
    echo "         - Comment out 'export ANTHROPIC_API_KEY=…' in"
    echo "           ~/.zshrc or ~/.bashrc"
    echo "         - Run: claude /login  → 'Log in with Claude.ai account'"
    echo "         - Verify: claude /status"
    echo ""
    echo "  To proceed anyway with API mode (you'll be billed), set"
    echo "  CLAUDE_API_MODE_ACK=1 in your environment and re-run."
    echo "============================================================"
    if [[ "${CLAUDE_API_MODE_ACK:-0}" != "1" ]]; then
      echo "Aborting. Re-run with CLAUDE_API_MODE_ACK=1 to bypass this check."
      exit 3
    fi
    echo "[v10.12] CLAUDE_API_MODE_ACK=1 — proceeding with API mode (billed)."
    echo ""
  fi

  if [[ "$ENGINE_MODEL_CHECK_MODE" == "dynamic" ]]; then
    MODELS_OUTPUT="$($ENGINE_MODELS_LIST_CMD 2>/dev/null || true)"
    if [[ -z "$MODELS_OUTPUT" ]]; then
      echo "ERROR: Could not fetch model list from: $ENGINE_MODELS_LIST_CMD"
      exit 1
    fi
    for agent in "${AGENTS[@]}"; do
      model="$(get_agent_model "$agent")"
      if ! echo "$MODELS_OUTPUT" | grep -Fq "$model"; then
        echo "ERROR: Model for $agent not found in engine: $model"
        echo "Run: $ENGINE_MODELS_LIST_CMD"
        echo "Then edit: $ENGINE_CFG"
        exit 2
      fi
    done
  elif [[ "$ENGINE_MODEL_CHECK_MODE" == "static" ]]; then
    for agent in "${AGENTS[@]}"; do
      model="$(get_agent_model "$agent")"
      found=false
      for known in $ENGINE_KNOWN_MODELS; do
        if [[ "$known" == "$model" ]]; then found=true; break; fi
      done
      if ! $found; then
        echo "ERROR: Model for $agent ($model) not in ENGINE_KNOWN_MODELS for $ENGINE."
        echo "Known: $ENGINE_KNOWN_MODELS"
        echo "Edit:  $ENGINE_CFG"
        exit 2
      fi
    done
  fi
fi

# ---------- engine config file (per-engine policy) ----------
# OpenCode: .opencode/config.json   |   Claude: .claude/settings.json
ENGINE_CONFIG_ABS="$PROJECT_DIR/$ENGINE_CONFIG_PATH"
mkdir -p "$(dirname "$ENGINE_CONFIG_ABS")"
case "$ENGINE" in
  opencode)
    cat > "$ENGINE_CONFIG_ABS" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": "allow",
    "edit": "allow",
    "webfetch": "allow"
  },
  "agent": {
    "build": { "tools": { "task": false, "general-task": false } },
    "plan":  { "tools": { "task": false, "general-task": false } }
  }
}
EOF
    cp "$ENGINE_CONFIG_ABS" "$PROJECT_DIR/opencode.json"  # mirror for forks
    ;;
  claude)
    cat > "$ENGINE_CONFIG_ABS" <<'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(bash:*)", "Bash(tmux:*)", "Bash(git:*)",
      "Bash(opencode:*)", "Bash(claude:*)", "Bash(docker:*)",
      "Bash(curl:*)", "Bash(npm:*)", "Bash(pip:*)",
      "Bash(pytest:*)", "Bash(node:*)",
      "Bash(grep:*)", "Bash(sed:*)", "Bash(awk:*)", "Bash(cut:*)",
      "Bash(find:*)", "Bash(wc:*)", "Bash(date:*)", "Bash(pwd:*)",
      "Bash(ls:*)", "Bash(cat:*)", "Bash(echo:*)", "Bash(printf:*)",
      "Bash(basename:*)", "Bash(dirname:*)", "Bash(head:*)", "Bash(tail:*)",
      "Bash(mkdir:*)", "Bash(rm:*)", "Bash(cp:*)", "Bash(mv:*)",
      "Bash(chmod:*)", "Bash(stat:*)", "Bash(test:*)",
      "Bash(true:*)", "Bash(false:*)", "Bash(:*)",
      "Bash(source:*)", "Bash(.:*)",
      "Read", "Write", "Edit", "WebFetch"
    ],
    "deny": [ "Task" ]
  }
}
EOF
    ;;
esac
echo "[v10.12] Engine = $ENGINE"
echo "[v10.12] Wrote engine config: $ENGINE_CONFIG_ABS"

# Mirror AGENTS.md → ENGINE_AUTO_CONTEXT_FILE if different
if [[ "$ENGINE_AUTO_CONTEXT_FILE" != "AGENTS.md" ]] && [[ -f AGENTS.md ]]; then
  # Replace placeholder header in CLAUDE.md with actual AGENTS.md content.
  cp AGENTS.md "$ENGINE_AUTO_CONTEXT_FILE"
  echo "[v10.12] Synced AGENTS.md → $ENGINE_AUTO_CONTEXT_FILE for Claude Code auto-load"
fi

# ---------- session-state file ----------
: > .agent_panes
mkdir -p .agent_boot_prompts .agent_tasks .agent_logs .pane_tasks .pane_logs memory

# Detect RESUME vs FRESH (v10.5 logic preserved)
RESUME_MODE=false
RESUME_REASON=""
if [[ -d memory ]]; then
  for f in memory/*.md; do
    [[ -f "$f" ]] || continue
    sz=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
    if [[ -n "$sz" ]] && (( sz > 400 )); then
      RESUME_MODE=true
      RESUME_REASON="non-empty $f detected"
      break
    fi
  done
fi
if ! $RESUME_MODE; then
  if find docs -type f -name '*.md' 2>/dev/null | xargs -I{} wc -c {} 2>/dev/null \
      | awk '$1 > 400 { found=1 } END { exit (found?0:1) }'; then
    RESUME_MODE=true
    RESUME_REASON="substantive docs/ found"
  fi
fi
if $RESUME_MODE; then
  echo "[v10.12] RESUME mode — $RESUME_REASON"
  echo "[v10.12] Orchestrator will run scripts/rescan_project.sh on first turn."
else
  echo "[v10.12] FRESH project — no prior memory or docs detected."
fi
echo "$([ $RESUME_MODE = true ] && echo RESUME || echo FRESH)" > .agent_session_mode

{
  echo "SESSION_NAME=${SESSION_NAME}"
  echo "PROJECT_DIR=${PROJECT_DIR}"
  echo "TEMPLATE_VERSION=10.12"
  echo "ENGINE=${ENGINE}"
  echo "AUTO_START_ORCHESTRATOR=${AUTO_START_ORCHESTRATOR}"
  echo "AUTO_START_WORKER_AGENTS=${AUTO_START_WORKER_AGENTS}"
  echo "ENGINE_CONFIG_ABS=${ENGINE_CONFIG_ABS}"
} > .agent_session

# Generate boot prompts for each agent
for AGENT in "${AGENTS[@]}"; do
  FULL_MODEL="$(get_agent_model "$AGENT")"
  bash scripts/agent_boot_prompt.sh "$AGENT" "$FULL_MODEL" \
    > ".agent_boot_prompts/${AGENT}.txt"
done

# ---------- helpers for engine-specific pane setup ----------
# Returns the export+launch prefix that puts engine config into env, if needed.
engine_env_prefix() {
  if [[ -n "$ENGINE_CONFIG_ENV_VAR" ]]; then
    echo "export ${ENGINE_CONFIG_ENV_VAR}='${ENGINE_CONFIG_ABS}';"
  fi
}

engine_tui_launch_cmd() {
  local model="$1"
  local prefix
  prefix="$(engine_env_prefix)"
  if [[ -n "$prefix" ]]; then
    echo "${prefix} ${ENGINE_TUI_LAUNCH} ${ENGINE_MODEL_FLAG} '${model}' ${OPENCODE_EXTRA_ARGS}"
  else
    echo "${ENGINE_TUI_LAUNCH} ${ENGINE_MODEL_FLAG} '${model}' ${OPENCODE_EXTRA_ARGS}"
  fi
}

# ---------- create 3 windows ----------
# Window 0 — OC (ORCHESTRATOR alone)
tmux new-session -d -s "$SESSION_NAME" -n "OC" -c "$PROJECT_DIR"

# Window 1 — DESIGN (PM, SA, BA, UX) — 2×2 tiled
tmux new-window -t "$SESSION_NAME:1" -n "DESIGN" -c "$PROJECT_DIR"
tmux split-window -h -t "$SESSION_NAME:1.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:1.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:1.2" -c "$PROJECT_DIR"
tmux select-layout -t "$SESSION_NAME:1" tiled

# Window 2 — DEV (BE, FE, QA, DELIVERY) — 2×2 tiled
tmux new-window -t "$SESSION_NAME:2" -n "DEV" -c "$PROJECT_DIR"
tmux split-window -h -t "$SESSION_NAME:2.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:2.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:2.2" -c "$PROJECT_DIR"
tmux select-layout -t "$SESSION_NAME:2" tiled

# Status bar — show all 3 windows + engine + notif count.
# v10.12 fix: pane-border-status / pane-border-format are WINDOW-scoped
# options. Setting them with `-t <session>` only applies to the
# currently-selected window at that moment (typically the last one
# created). To get pane titles in ALL 3 windows we must set them
# per-window via set-window-option.
for win in 0 1 2; do
  tmux set-window-option -t "$SESSION_NAME:$win" pane-border-status top
  tmux set-window-option -t "$SESSION_NAME:$win" pane-border-format " #{pane_title} "
done
# Session-level (status bar): these ARE session-scoped, so single set is fine.
tmux set-option -t "$SESSION_NAME" status-left-length 80
tmux set-option -t "$SESSION_NAME" status-left "[#S | ${ENGINE}] "
tmux set-option -t "$SESSION_NAME" status-right "#(date '+%H:%M %d-%b')"

# ---------- assign role → pane_id ----------
# Window 0: ORCHESTRATOR
# Window 1: PM (pane index 0), SA (1), BA (2), UX (3)
# Window 2: BE (0), FE (1), QA (2), DELIVERY (3)
get_pane_id_at() {
  local win="$1" idx="$2"
  tmux list-panes -t "${SESSION_NAME}:${win}" -F "#{pane_index}:#{pane_id}" \
    | sort -n | sed -n "$((idx + 1))p" | cut -d: -f2
}

# Mapping
assign_role() {
  local role="$1" win="$2" idx="$3"
  local pane_id
  pane_id="$(get_pane_id_at "$win" "$idx")"
  echo "${role}=${pane_id}" >> .agent_panes
  tmux select-pane -t "$pane_id" -T "${role}"
  echo "  ${role} → window ${win} pane ${idx} (${pane_id})"
}

echo "[v10.12] Pane assignments:"
assign_role ORCHESTRATOR 0 0
assign_role PM           1 0
assign_role SA           1 1
assign_role BA           1 2
assign_role UX           1 3
assign_role BE           2 0
assign_role FE           2 1
assign_role QA           2 2
assign_role DELIVERY     2 3

# ---------- initial bootstrap per pane ----------
for AGENT in "${AGENTS[@]}"; do
  FULL_MODEL="$(get_agent_model "$AGENT")"
  PANE_ID="$(grep "^${AGENT}=" .agent_panes | cut -d= -f2-)"

  tmux send-keys -t "$PANE_ID" "cd '$PROJECT_DIR'" C-m
  tmux send-keys -t "$PANE_ID" "export PROJECT_NAME='$SESSION_NAME'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_NAME='$AGENT'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_MODEL='$FULL_MODEL'" C-m
  tmux send-keys -t "$PANE_ID" "export ENGINE='$ENGINE'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_SESSION_MODE='$([ $RESUME_MODE = true ] && echo RESUME || echo FRESH)'" C-m
  if [[ -n "$ENGINE_CONFIG_ENV_VAR" ]]; then
    tmux send-keys -t "$PANE_ID" "export ${ENGINE_CONFIG_ENV_VAR}='${ENGINE_CONFIG_ABS}'" C-m
  fi

  if [[ "$SHOW_AGENT_BANNER" == "true" ]]; then
    tmux send-keys -t "$PANE_ID" "bash scripts/agent_banner.sh '$AGENT' '$FULL_MODEL' '$SESSION_NAME'" C-m
  fi

  if [[ "$AGENT" == "ORCHESTRATOR" && "$AUTO_START_ORCHESTRATOR" == "true" ]]; then
    tmux send-keys -t "$PANE_ID" "echo '[v10.12] Engine=${ENGINE} | launching ${ENGINE_TUI_LAUNCH} for ORCHESTRATOR (model=${FULL_MODEL})'" C-m
    tmux send-keys -t "$PANE_ID" "echo '[v10.12] Auto-relaunch on exit — press Enter to relaunch, Ctrl+C/Ctrl+D for shell.'" C-m
    LAUNCH=$(engine_tui_launch_cmd "$FULL_MODEL")
    LAUNCH_LOOP="while :; do ${LAUNCH}; rc=\$?; printf '\\n[v10.12] ${ENGINE_BINARY} exited (rc=%s).\\n  Press <Enter> to relaunch, or Ctrl+C / Ctrl+D to stay at shell.\\n' \"\$rc\"; if ! read -r _; then break; fi; done"
    tmux send-keys -t "$PANE_ID" "$LAUNCH_LOOP" C-m

    if $RESUME_MODE; then
      KICKOFF="[RESUME] Session resumed (memory/ exists). Your VERY FIRST action: run 'bash scripts/rescan_project.sh' to see where the team left off, then greet the user in 3-5 short bullets summarising current phase, active workstreams, pending questions, and the last deployed URL. Do not start any new phase until the user confirms direction."
      (
        sleep 8
        tmux send-keys -t "$PANE_ID" "$KICKOFF" 2>/dev/null || true
        sleep 0.3
        tmux send-keys -t "$PANE_ID" C-m 2>/dev/null || true
      ) &
    fi
  else
    if [[ "$AUTO_START_WORKER_AGENTS" == "true" ]]; then
      tmux send-keys -t "$PANE_ID" "echo '[v10.12] AUTO_START_WORKER_AGENTS=true is not recommended; workers stay idle until routed.'" C-m
      LAUNCH=$(engine_tui_launch_cmd "$FULL_MODEL")
      tmux send-keys -t "$PANE_ID" "$LAUNCH" C-m
    else
      tmux send-keys -t "$PANE_ID" "echo '[v10.12] Worker pane ready (engine=${ENGINE}). Will be activated by  bash scripts/route_to_pane.sh ${AGENT} \"...\".'" C-m
    fi
  fi
done

# Focus pane 0 of window 0 (ORCHESTRATOR), select OC window
tmux select-window -t "$SESSION_NAME:0"
tmux select-pane -t "$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2-)"
tmux attach -t "$SESSION_NAME"
