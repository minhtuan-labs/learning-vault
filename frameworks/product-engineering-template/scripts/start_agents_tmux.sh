#!/usr/bin/env bash
set -euo pipefail

# v10.1 — Start the 9-pane tmux session for the product engineering workflow.
#
# Key fixes vs v9/v10.0:
#   - Do NOT pass --config to opencode. The opencode-go fork doesn't accept
#     that flag and exits with an error, which made the Orchestrator pane
#     drop back to bash and (in v10.0) get a racy boot-prompt paste that
#     left it stuck at  dquote>  .
#   - Rely on (a) OPENCODE_CONFIG=<path> env var, and (b) opencode's
#     auto-load of .opencode/config.json and opencode.json from the
#     project root. Both mechanisms are supported by SST OpenCode and
#     by opencode-go.
#   - Do NOT auto-paste a boot prompt into the Orchestrator pane. Instead
#     OpenCode auto-loads AGENTS.md at startup, which contains the
#     role-aware instructions (Orchestrator + every worker role).
#   - If you ever need to inject a boot prompt manually after OpenCode
#     TUI is loaded, run: bash scripts/inject_boot_prompt.sh ORCHESTRATOR

INPUT_PROJECT_NAME="${1:-}"
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
AGENTS=(ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY)

MODEL_CONFIG_FILE="config/agent_models.env"
if [[ -f "$MODEL_CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$MODEL_CONFIG_FILE"
else
  echo "Missing $MODEL_CONFIG_FILE"
  exit 1
fi

OPENCODE_CONFIG_FILE="config/opencode.env"
if [[ -f "$OPENCODE_CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$OPENCODE_CONFIG_FILE"
fi

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

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Session '$SESSION_NAME' already exists."
  echo "Attach with: tmux attach -t '$SESSION_NAME'"
  exit 0
fi

# Strict model validation
if [[ "$STRICT_MODEL_CHECK" == "true" ]]; then
  if ! command -v opencode >/dev/null 2>&1; then
    echo "ERROR: opencode command not found. Install OpenCode or set AUTO_START_ORCHESTRATOR=false in config/opencode.env"
    exit 1
  fi

  MODELS_OUTPUT="$(opencode models 2>/dev/null || true)"
  if [[ -z "$MODELS_OUTPUT" ]]; then
    echo "ERROR: Could not fetch 'opencode models'."
    echo "Run manually: opencode models"
    exit 1
  fi

  for agent in "${AGENTS[@]}"; do
    model="$(get_agent_model "$agent")"
    if ! echo "$MODELS_OUTPUT" | grep -Fq "$model"; then
      echo "ERROR: Configured model for $agent not found: $model"
      echo "Run: opencode models"
      echo "Then edit: config/agent_models.env"
      exit 2
    fi
  done
fi

# v10.1: regenerate the OpenCode config in two locations so autoload works
# whether your opencode fork looks for .opencode/config.json or opencode.json
# at project root.
OPENCODE_CONFIG_PATH="$PROJECT_DIR/.opencode/config.json"
mkdir -p "$PROJECT_DIR/.opencode"
cat > "$OPENCODE_CONFIG_PATH" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": "allow",
    "edit": "allow",
    "webfetch": "allow"
  },
  "agent": {
    "build": {
      "tools": {
        "task": false,
        "general-task": false
      }
    },
    "plan": {
      "tools": {
        "task": false,
        "general-task": false
      }
    }
  }
}
EOF
# Mirror as opencode.json at project root for forks that prefer that name.
cp "$OPENCODE_CONFIG_PATH" "$PROJECT_DIR/opencode.json"
echo "[v10.1] Wrote OpenCode config:"
echo "        $OPENCODE_CONFIG_PATH"
echo "        $PROJECT_DIR/opencode.json (mirror)"
echo "[v10.1] AGENTS.md at $PROJECT_DIR/AGENTS.md will be auto-loaded by OpenCode."

tmux new-session -d -s "$SESSION_NAME" -n agents -c "$PROJECT_DIR"

# Make 9 panes in a tiled grid.
tmux split-window -h -t "$SESSION_NAME:0.0" -c "$PROJECT_DIR"
tmux split-window -h -t "$SESSION_NAME:0.1" -c "$PROJECT_DIR"
tmux select-layout -t "$SESSION_NAME:0" even-horizontal

tmux split-window -v -t "$SESSION_NAME:0.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:0.1" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:0.2" -c "$PROJECT_DIR"
tmux select-layout -t "$SESSION_NAME:0" tiled

tmux split-window -v -t "$SESSION_NAME:0.0" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:0.2" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION_NAME:0.4" -c "$PROJECT_DIR"
tmux select-layout -t "$SESSION_NAME:0" tiled

tmux set-option -t "$SESSION_NAME" pane-border-status top
tmux set-option -t "$SESSION_NAME" pane-border-format " #{pane_title} "
tmux set-option -t "$SESSION_NAME" status-left-length 80
tmux set-option -t "$SESSION_NAME" status-left "[#S] "
tmux set-option -t "$SESSION_NAME" status-right "#(date '+%H:%M %d-%b')"

: > .agent_panes
mkdir -p .agent_boot_prompts .agent_tasks .agent_logs .pane_tasks .pane_logs memory

# v10.5: detect whether this is a RESUME or a FRESH start by inspecting
# memory/ and docs/. Resume mode tells the Orchestrator (via an env var
# exported into pane 1) to run scripts/rescan_project.sh on the very
# first user turn and recap progress instead of treating the request as
# a brand-new project.
RESUME_MODE=false
RESUME_REASON=""
if [[ -d memory ]]; then
  # Any role memory file with more than the boilerplate skeleton (> 400 bytes)?
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
  # Also resume if docs/ has substantive content even without memory/.
  if find docs -type f -name '*.md' 2>/dev/null | xargs -I{} wc -c {} 2>/dev/null \
      | awk '$1 > 400 { found=1 } END { exit (found?0:1) }'; then
    RESUME_MODE=true
    RESUME_REASON="substantive docs/ found"
  fi
fi
if $RESUME_MODE; then
  echo "[v10.5] RESUME mode — $RESUME_REASON"
  echo "[v10.5] Orchestrator will run scripts/rescan_project.sh on first turn"
  echo "[v10.5] to recap progress instead of treating this as a fresh project."
else
  echo "[v10.5] FRESH project — no prior memory or docs detected."
fi
# Record the mode so Orchestrator's prompt-time env can read it.
echo "$([ $RESUME_MODE = true ] && echo RESUME || echo FRESH)" > .agent_session_mode

{
  echo "SESSION_NAME=${SESSION_NAME}"
  echo "PROJECT_DIR=${PROJECT_DIR}"
  echo "TEMPLATE_VERSION=10.1"
  echo "AUTO_START_ORCHESTRATOR=${AUTO_START_ORCHESTRATOR}"
  echo "AUTO_START_WORKER_AGENTS=${AUTO_START_WORKER_AGENTS}"
  echo "OPENCODE_CONFIG_PATH=${OPENCODE_CONFIG_PATH}"
} > .agent_session

# Build a per-pane boot prompt file (used only if user runs
# scripts/inject_boot_prompt.sh manually after the TUI is up).
for AGENT in "${AGENTS[@]}"; do
  FULL_MODEL="$(get_agent_model "$AGENT")"
  bash scripts/agent_boot_prompt.sh "$AGENT" "$FULL_MODEL" \
    > ".agent_boot_prompts/${AGENT}.txt"
done

for i in "${!AGENTS[@]}"; do
  AGENT="${AGENTS[$i]}"
  FULL_MODEL="$(get_agent_model "$AGENT")"

  PANE_ID=$(tmux list-panes -t "$SESSION_NAME:0" -F "#{pane_index}:#{pane_id}" | sort -n | sed -n "$((i+1))p" | cut -d: -f2)
  tmux select-pane -t "$PANE_ID" -T "$((i+1))-$AGENT"
  echo "${AGENT}=${PANE_ID}" >> .agent_panes

  tmux send-keys -t "$PANE_ID" "cd '$PROJECT_DIR'" C-m
  tmux send-keys -t "$PANE_ID" "export PROJECT_NAME='$SESSION_NAME'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_NAME='$AGENT'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_MODEL='$FULL_MODEL'" C-m
  tmux send-keys -t "$PANE_ID" "export OPENCODE_FULL_MODEL='$FULL_MODEL'" C-m
  tmux send-keys -t "$PANE_ID" "export OPENCODE_CONFIG='$OPENCODE_CONFIG_PATH'" C-m
  tmux send-keys -t "$PANE_ID" "export AGENT_SESSION_MODE='$([ $RESUME_MODE = true ] && echo RESUME || echo FRESH)'" C-m

  if [[ "$SHOW_AGENT_BANNER" == "true" ]]; then
    tmux send-keys -t "$PANE_ID" "bash scripts/agent_banner.sh '$AGENT' '$FULL_MODEL' '$SESSION_NAME'" C-m
  fi

  if [[ "$AGENT" == "ORCHESTRATOR" && "$AUTO_START_ORCHESTRATOR" == "true" ]]; then
    # Launch OpenCode interactively and AUTO-RELAUNCH on exit. The
    # Orchestrator pane is the user's primary chat session; if opencode
    # ever exits (model hiccup, tool-call error, etc.) we don't want the
    # user dropped silently to bash. The while-loop offers a quick
    # confirmation before relaunching so the user can still abort if
    # they really want a shell.
    tmux send-keys -t "$PANE_ID" "echo '[v10.2] Launching Orchestrator OpenCode (model=$FULL_MODEL). Will auto-relaunch on exit.'" C-m
    tmux send-keys -t "$PANE_ID" "echo '[v10.2] AGENTS.md is auto-loaded by OpenCode.'" C-m
    # Build the launch command as a single line. If opencode exits with
    # any non-zero rc or even rc=0, prompt user to relaunch. Pressing
    # Ctrl+C at the prompt or EOF (Ctrl+D) breaks the loop.
    LAUNCH_CMD="while :; do opencode --model '$FULL_MODEL' $OPENCODE_EXTRA_ARGS; rc=\$?; printf '\\n[v10.2] opencode exited (rc=%s).\\n  Press <Enter> to relaunch, or Ctrl+C / Ctrl+D to stay at shell.\\n' \"\$rc\"; if ! read -r _; then break; fi; done"
    tmux send-keys -t "$PANE_ID" "$LAUNCH_CMD" C-m

    # If resuming, send a kickoff message to the Orchestrator TUI a few
    # seconds after opencode loads. This is essentially an [INBOX]-style
    # auto-ping, but for "session resumed" instead of a worker question.
    if $RESUME_MODE; then
      KICKOFF="[RESUME] Session resumed (memory/ exists from a prior run). Your VERY FIRST action: run 'bash scripts/rescan_project.sh' to see where the team left off, then greet the user in 3-5 short bullets summarising current phase, who is mid-task, any pending questions, and the last deployed URL if any. Do not start any new phase until the user confirms direction."
      (
        sleep 8
        tmux send-keys -t "$PANE_ID" "$KICKOFF" 2>/dev/null || true
        sleep 0.3
        tmux send-keys -t "$PANE_ID" C-m 2>/dev/null || true
      ) &
    fi
  else
    if [[ "$AUTO_START_WORKER_AGENTS" == "true" ]]; then
      tmux send-keys -t "$PANE_ID" "echo '[v10.1] AUTO_START_WORKER_AGENTS=true is not recommended; workers should stay idle until routed.'" C-m
      tmux send-keys -t "$PANE_ID" "opencode --model '$FULL_MODEL' $OPENCODE_EXTRA_ARGS" C-m
    else
      tmux send-keys -t "$PANE_ID" "echo '[v10.1] Worker pane ready. Will be activated by  bash scripts/route_to_pane.sh $AGENT \"...\".'" C-m
    fi
  fi
done

tmux select-pane -t "$(grep '^ORCHESTRATOR=' .agent_panes | cut -d= -f2-)"
tmux attach -t "$SESSION_NAME"
