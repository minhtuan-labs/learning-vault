#!/usr/bin/env bash
set -euo pipefail

# v10 — Route a task from Orchestrator to another tmux pane.
#
# Key v10 fixes compared to v9:
#   - Stops using the non-existent env var OPENCODE_CONFIG_CONTENT.
#   - Writes a real OpenCode config file at .opencode/config.json and passes it
#     via the standard --config flag AND the OPENCODE_CONFIG env var (file path).
#   - Disables the built-in Task / general-task subagent tool through the
#     correct schema:  agent.<mode>.tools.task = false
#   - Emits a verifiable log line so verify_routing.sh can confirm the routing
#     actually fired (a real shell command, not just a chat message).

TARGET="${1:-}"
MESSAGE="${2:-}"

if [[ -z "$TARGET" || -z "$MESSAGE" ]]; then
  echo "Usage: bash scripts/route_to_pane.sh <PANE_ROLE> \"message\""
  echo "Roles: PM SA BA UX BE FE QA DELIVERY"
  echo "(ORCHESTRATOR is intentionally NOT routable — see below.)"
  exit 1
fi

# v10.2: never route to the Orchestrator pane. The Orchestrator pane runs
# an interactive OpenCode TUI; sending Ctrl+C + new bash commands into it
# would terminate the user's chat session. Workers that need user input
# must use scripts/ask_orchestrator.sh, not route_to_pane.sh.
if [[ "$TARGET" == "ORCHESTRATOR" ]]; then
  echo "ERROR: route_to_pane.sh refuses to target ORCHESTRATOR."
  echo "       The Orchestrator pane is the user's interactive session."
  echo "       Workers needing user input must call:"
  echo "           bash scripts/ask_orchestrator.sh <YOUR_ROLE> \"<question>\""
  echo "       The Orchestrator answers via:"
  echo "           bash scripts/answer_role.sh <ROLE> <question_id> \"<answer>\""
  exit 2
fi

MAP_FILE=".agent_panes"
SESSION_FILE=".agent_session"

if [[ ! -f "$MAP_FILE" ]]; then
  echo "Missing .agent_panes. Run scripts/start_agents_tmux.sh <project_name> first."
  exit 1
fi

# v10.12 — read engine choice from .agent_session
ENGINE="opencode"  # fallback
if [[ -f "$SESSION_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$SESSION_FILE"
fi
ENGINE_CFG="config/engines/${ENGINE}.env"
if [[ ! -f "$ENGINE_CFG" ]]; then
  echo "Missing engine config: $ENGINE_CFG"
  exit 1
fi
# shellcheck disable=SC1090
source "$ENGINE_CFG"

ENGINE_CONFIG_ABS="$(pwd)/${ENGINE_CONFIG_PATH}"
if [[ ! -f "$ENGINE_CONFIG_ABS" ]]; then
  echo "Missing $ENGINE_CONFIG_ABS"
  echo "Run scripts/start_agents_tmux.sh first; it regenerates the config."
  exit 1
fi

if [[ -f "config/opencode.env" ]]; then
  # shellcheck disable=SC1090
  source "config/opencode.env"
fi

WORKER_OPENCODE_MODE="${WORKER_OPENCODE_MODE:-run}"

PANE_ID=$(grep "^${TARGET}=" "$MAP_FILE" | cut -d= -f2- || true)

if [[ -z "$PANE_ID" ]]; then
  echo "Unknown pane role: $TARGET"
  echo "Known pane roles:"
  cut -d= -f1 "$MAP_FILE"
  exit 1
fi

MODEL_VAR="${TARGET}_MODEL"
TARGET_MODEL="${!MODEL_VAR:-}"

if [[ -z "$TARGET_MODEL" ]]; then
  echo "No model configured for $TARGET in engine $ENGINE. Expected variable: $MODEL_VAR in $ENGINE_CFG"
  exit 1
fi

if ! command -v "$ENGINE_BINARY" >/dev/null 2>&1; then
  echo "ERROR: engine binary '$ENGINE_BINARY' not found in PATH."
  exit 1
fi

mkdir -p .pane_tasks .pane_logs .agent_tasks .agent_logs

# v10.6 — role-specific lean read lists.
# Each role only reads what its job actually needs, not the whole project.
# memory/<ROLE>.md + memory/_PROJECT_STATE.md carry cross-role context, so
# we no longer make every worker re-read 10+ governance / config / other-
# role files every time.
get_role_read_list() {
  case "$1" in
    PM)
      echo "PRODUCT_IDEA.md docs/product/PRD.md docs/product/ROADMAP.md planning/BACKLOG.md planning/OPEN_QUESTIONS.md docs/business/USER_STORIES.md"
      ;;
    SA)
      echo "PRODUCT_IDEA.md docs/product/PRD.md docs/business/USER_STORIES.md docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/architecture/ADR.md docs/architecture/API_CONTRACT.md"
      ;;
    BA)
      echo "PRODUCT_IDEA.md docs/product/PRD.md docs/business/BUSINESS_REQUIREMENTS.md docs/business/USER_STORIES.md docs/business/DOMAIN_MODEL.md"
      ;;
    UX)
      echo "PRODUCT_IDEA.md docs/product/PRD.md docs/product/UX_FLOW.md docs/product/WIREFRAMES.md docs/product/DESIGN_NOTES.md docs/business/USER_STORIES.md"
      ;;
    BE)
      echo "docs/architecture/API_CONTRACT.md docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/business/USER_STORIES.md planning/BE_PLAN.md planning/BACKLOG.md"
      ;;
    FE)
      echo "docs/product/UX_FLOW.md docs/product/WIREFRAMES.md docs/product/DESIGN_NOTES.md docs/architecture/API_CONTRACT.md planning/FE_PLAN.md planning/BACKLOG.md"
      ;;
    QA)
      echo "docs/qa/TEST_PLAN.md docs/qa/TEST_CASES.md docs/business/USER_STORIES.md docs/architecture/API_CONTRACT.md planning/BACKLOG.md reports/TEST_REPORT.md reports/BUG_REPORT.md"
      ;;
    DELIVERY)
      echo "docs/architecture/TECH_STACK.md planning/BE_PLAN.md planning/FE_PLAN.md docs/delivery/DELIVERY_PLAN.md docs/delivery/RUNNING_APP.md docs/delivery/RELEASE_NOTES.md reports/TEST_REPORT.md"
      ;;
    *)
      echo ""
      ;;
  esac
}

# Build a bullet-formatted read list, but only include files that ACTUALLY
# EXIST in the project right now — keeps task files honest and small.
build_role_read_list_md() {
  local role="$1"
  local raw
  raw="$(get_role_read_list "$role")"
  for f in $raw; do
    if [[ -f "$f" ]]; then
      sz=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
      if [[ -n "$sz" ]] && (( sz > 50 )); then
        printf -- "- %s\n" "$f"
      else
        printf -- "- %s   (empty / skeleton — skim only if needed)\n" "$f"
      fi
    else
      printf -- "- %s   (does not exist yet — create if your task requires it)\n" "$f"
    fi
  done
}

ROLE_READ_LIST_MD="$(build_role_read_list_md "$TARGET")"

TS="$(date +%Y%m%d_%H%M%S)"
TASK_FILE=".pane_tasks/${TARGET}_${TS}.md"
LOG_FILE=".pane_logs/${TARGET}_${TS}.log"
ROUTING_RECEIPT=".pane_logs/_routing_receipts.log"

cat > "$TASK_FILE" <<EOF
You are running in the $TARGET tmux pane for this product engineering project.

Your configured model is: $TARGET_MODEL.

# STEP 0 — fail fast if your upstream inputs are missing (DO NOT SKIP)

Before reading anything else, run:

    bash scripts/check_prerequisites.sh $TARGET

If exit code is 0, continue to STEP 1.

If exit code is 1 (one or more inputs are missing or skeleton-only),
you MUST stop and hand back to the Orchestrator instead of trying to
fake the missing context. Follow the guidance printed by the script:

  • If a USER-owned file (e.g. PRODUCT_IDEA.md) is missing, run:
        bash scripts/ask_orchestrator.sh $TARGET "<question stating what is missing>"

  • If an agent-owned file is missing, run:
        bash scripts/notify_orchestrator.sh $TARGET "Cannot proceed — missing inputs: <comma-separated list>. Need <upstream owners> to produce them first. Please coordinate and re-route me when ready."

Then append a "blocked on missing inputs" entry to memory/$TARGET.md
and exit the OpenCode turn. DO NOT write placeholder / best-guess
content for files another role owns, and DO NOT generate "TBD"
sections that fake the dependency.

# STEP 1 — read durable memory FIRST (this is your continuity layer)

Before anything else, read these two files. They contain decisions
and state from previous sessions — without them you'll re-invent
choices the team already made.

- memory/_PROJECT_STATE.md     — what's the team's overall state
- memory/$TARGET.md            — what you ($TARGET) decided previously

If either is missing or empty, that just means this is a fresh
project. Note it and move on.

# STEP 2 — read your role prompt + a LEAN, role-specific file list

Read in order (skip files that don't exist or are skeletons):

- prompts/agents/$TARGET.md  (your system prompt — re-skim if you've
                              been routed many tasks today)
- TASK.md                    (current phase / status)
- AGENTS.md                  (only re-skim if its content was updated
                              since session start)

Then the role-specific list for $TARGET:

$ROLE_READ_LIST_MD

## DO NOT read by default

Reading more files = more tokens = more cost. Do NOT read the files
below unless your TASK explicitly mentions them:

- prompts/agents/<OTHER_ROLES>.md   (governance for them, not you)
- planning/PANE_ROUTING_RULES.md    (governance — already in AGENTS.md)
- planning/AGENT_WORKFLOW.md        (governance)
- planning/ORCHESTRATOR_RUNTIME_RULES.md  (Orchestrator-only)
- config/AGENT_MODELS.md            (model mapping — not your concern)
- config/OPENCODE_PERMISSION_POLICY.md  (config)
- VERSION.md, README.md             (meta / external readers)
- .pane_logs/*, .pane_tasks/*       (your own debugging only)

If the task description forces you to look at a file outside this
list, that's fine — just don't over-read defensively.

memory/_PROJECT_STATE.md and memory/$TARGET.md already carry the
cross-role context you'd otherwise re-derive from those skipped files.

# STEP 3 — do the work

Task from caller:
$MESSAGE

Execution requirements:
- Actually create/update the requested files.
- Keep output concise and action-oriented.
- The Task / general-task subagent tool is disabled by .opencode/config.json.
- Do not simulate another pane role inside your own response.
- If another pane role should act next, execute a real shell command:
    bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
- If you need a user decision, do not guess:
    bash scripts/ask_orchestrator.sh $TARGET "<question>"
- If you have a status event to surface to the user, file a notification:
    bash scripts/notify_orchestrator.sh $TARGET "<one-line subject>"

# STEP 4 — update memory before you exit (MANDATORY)

Before ending this OpenCode turn, append a dated entry to
memory/$TARGET.md describing:

- decisions you made in this task that affect future work
- conventions you established (naming, error format, port, etc.)
- gotchas / footguns you hit
- open items you're tracking that don't fit BACKLOG yet

Use this format:

    ### YYYY-MM-DD HH:MM — <short title>
    <2-5 line summary>

If nothing notable happened, append a single line:

    ### YYYY-MM-DD HH:MM — routine task, no new entries

NEVER exit silently without touching memory/$TARGET.md. Tomorrow's
session may load with no other clue of what happened today.

At the very end of your reply, state which files you changed
(including memory/$TARGET.md).
EOF

# Record a routing receipt so verify_routing.sh can prove the routing fired.
{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] route_to_pane.sh -> $TARGET (pane=$PANE_ID, model=$TARGET_MODEL)"
  echo "  task_file=$TASK_FILE"
  echo "  log_file=$LOG_FILE"
  echo "  message=$MESSAGE"
} >> "$ROUTING_RECEIPT"

# v10.12 — compose the worker command for the active engine.
# Both opencode and claude auto-load their config file from the project
# CWD (.opencode/config.json or .claude/settings.json). For engines that
# need an env var hint (opencode does), we prepend it.
ENGINE_ENV_PREFIX=""
if [[ -n "$ENGINE_CONFIG_ENV_VAR" ]]; then
  ENGINE_ENV_PREFIX="${ENGINE_CONFIG_ENV_VAR}='${ENGINE_CONFIG_ABS}' "
fi
TASK_PROMPT="Execute the routed pane task described in $TASK_FILE. Read the file, perform the work, update files as needed, and report completion. Do not use internal subagents (the task tool is disabled in $ENGINE_CONFIG_PATH and AGENTS.md)."
WORKER_CMD="${ENGINE_ENV_PREFIX}${ENGINE_RUN_BASE} ${ENGINE_MODEL_FLAG} '${TARGET_MODEL}' \"${TASK_PROMPT}\""

# v10.12 — Wrap the worker command in `script` so the engine sees a PTY
# (defeats stdio block-buffering). This gives LIVE streaming output in
# the pane WHILE still capturing everything to the log file. Without
# the PTY, opencode/claude buffer their output and the pane stays
# blank until the run completes.
#
# We write a temp shell wrapper to avoid nested-quote escaping nightmares.
WORKER_SH=".pane_tasks/_run_${TARGET}_${TS}.sh"
{
  echo "#!/bin/bash"
  echo "set -e"
  echo "$WORKER_CMD"
} > "$WORKER_SH"
chmod +x "$WORKER_SH"
WORKER_SH_ABS="$(pwd)/$WORKER_SH"

# Build invocation according to platform's `script` flavor.
if command -v script >/dev/null 2>&1; then
  if [[ "$(uname -s)" == "Darwin" ]]; then
    # macOS BSD script:  script [-q] LOGFILE COMMAND [ARGS...]
    INVOCATION="script -q '$LOG_FILE' '$WORKER_SH_ABS'"
  else
    # GNU util-linux script:  script -q -e -c COMMAND LOGFILE
    INVOCATION="script -q -e -c '$WORKER_SH_ABS' '$LOG_FILE'"
  fi
else
  # `script` not available — fall back to tee (output may buffer).
  INVOCATION="'$WORKER_SH_ABS' 2>&1 | tee '$LOG_FILE'"
fi

tmux send-keys -t "$PANE_ID" C-c
tmux send-keys -t "$PANE_ID" "cd '$(pwd)'" C-m
tmux send-keys -t "$PANE_ID" "clear" C-m
tmux send-keys -t "$PANE_ID" "bash scripts/agent_banner.sh '$TARGET' '$TARGET_MODEL' \"\${PROJECT_NAME:-unknown}\"" C-m
tmux send-keys -t "$PANE_ID" "echo '[v10.12] Running routed pane task: $TASK_FILE'" C-m
tmux send-keys -t "$PANE_ID" "echo '[v10.12] Log file: $LOG_FILE   (live output below + captured to log)'" C-m

if [[ "$WORKER_OPENCODE_MODE" == "run" ]]; then
  tmux send-keys -t "$PANE_ID" "$INVOCATION" C-m
else
  # TUI mode: also through script for live output
  TUI_CMD="${ENGINE_ENV_PREFIX}${ENGINE_TUI_LAUNCH} ${ENGINE_MODEL_FLAG} '${TARGET_MODEL}'"
  TUI_SH=".pane_tasks/_run_${TARGET}_${TS}_tui.sh"
  { echo "#!/bin/bash"; echo "$TUI_CMD"; } > "$TUI_SH"
  chmod +x "$TUI_SH"
  TUI_SH_ABS="$(pwd)/$TUI_SH"
  if command -v script >/dev/null 2>&1; then
    if [[ "$(uname -s)" == "Darwin" ]]; then
      TUI_INVOCATION="script -q '$LOG_FILE' '$TUI_SH_ABS'"
    else
      TUI_INVOCATION="script -q -e -c '$TUI_SH_ABS' '$LOG_FILE'"
    fi
  else
    TUI_INVOCATION="'$TUI_SH_ABS' 2>&1 | tee '$LOG_FILE'"
  fi
  tmux send-keys -t "$PANE_ID" "$TUI_INVOCATION" C-m
fi

# Backward compatible mirror for old tooling that reads .agent_tasks/.
cp "$TASK_FILE" ".agent_tasks/$(basename "$TASK_FILE")" 2>/dev/null || true

echo "[v10] Routed task to $TARGET pane (pane=$PANE_ID, model=$TARGET_MODEL)"
echo "      Task file: $TASK_FILE"
echo "      Log file : $LOG_FILE"
echo "      Receipt  : $ROUTING_RECEIPT"
