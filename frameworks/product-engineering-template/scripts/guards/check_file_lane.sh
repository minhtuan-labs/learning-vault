#!/usr/bin/env bash
# v10.23 — Pre-Write/Edit hook for Claude Code.
#
# Wired via .claude/settings.json:
#   "hooks": {
#     "PreToolUse": [
#       { "matcher": "Write|Edit",
#         "hooks": [{ "type": "command",
#                     "command": "bash scripts/guards/check_file_lane.sh" }] }
#     ]
#   }
#
# Closes the v10.19 loophole where Claude's Write/Edit tools bypassed
# the PATH guard (which only intercepts shell commands). Now the
# Orchestrator pane can't edit owner-specific files via tool calls
# either — the hook runs before every Write/Edit and rejects the call
# (exit 2) when the path belongs to another role.
#
# Worker panes (BE/FE/QA/DELIVERY/etc.) are unaffected — the hook
# checks $AGENT_NAME and only enforces when it equals ORCHESTRATOR.

set -u

# Worker panes — skip enforcement entirely.
if [[ "${AGENT_NAME:-}" != "ORCHESTRATOR" ]]; then
  exit 0
fi

# Read Claude's tool-input JSON from stdin.
INPUT=$(cat 2>/dev/null || true)

# Extract file_path. Use jq if available (most reliable), fall back
# to python3, then a grep/sed scrape.
FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
fi
if [[ -z "$FILE_PATH" ]] && command -v python3 >/dev/null 2>&1; then
  FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try:
  d=json.load(sys.stdin)
  print(d.get('tool_input',{}).get('file_path',''))
except Exception:
  pass" 2>/dev/null || true)
fi
if [[ -z "$FILE_PATH" ]]; then
  # Best-effort regex fallback. If we still can't get a path, allow
  # (don't break Orchestrator on hook parse failures).
  FILE_PATH=$(printf '%s' "$INPUT" \
              | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
              | head -1)
fi
[[ -z "$FILE_PATH" ]] && exit 0

# Normalise to project-relative path.
PROJECT_ROOT="$(pwd)"
REL_PATH="$FILE_PATH"
if [[ "$FILE_PATH" == "$PROJECT_ROOT/"* ]]; then
  REL_PATH="${FILE_PATH#$PROJECT_ROOT/}"
elif [[ "$FILE_PATH" == /* ]]; then
  # Absolute path outside project root — out of our jurisdiction; allow.
  exit 0
fi

# Allow-list: files Orchestrator IS permitted to edit directly.
case "$REL_PATH" in
  TASK.md|PRODUCT_IDEA.md) exit 0 ;;
  memory/_PROJECT_STATE.md|memory/ORCHESTRATOR.md) exit 0 ;;
  # Runtime artifacts under .pane_* / .agent_* / .pane_heartbeats/ etc.
  .pane_*|.agent_*|.watcher.pid) exit 0 ;;
esac

# Block-list: which role owns which path?
OWNER=""
ROLE=""
case "$REL_PATH" in
  backend/*|backend)
    OWNER="BE — backend code is BE's lane"; ROLE="BE" ;;
  frontend/*|frontend)
    OWNER="FE — frontend code is FE's lane"; ROLE="FE" ;;
  docs/product/PRD.md|docs/product/ROADMAP.md)
    OWNER="PM"; ROLE="PM" ;;
  planning/BACKLOG.md|planning/OPEN_QUESTIONS.md)
    OWNER="PM"; ROLE="PM" ;;
  planning/BE_PLAN.md)
    OWNER="BE"; ROLE="BE" ;;
  planning/FE_PLAN.md)
    OWNER="FE"; ROLE="FE" ;;
  docs/business/*)
    OWNER="BA"; ROLE="BA" ;;
  docs/architecture/*)
    OWNER="SA"; ROLE="SA" ;;
  docs/product/UX_FLOW.md|docs/product/WIREFRAMES.md|docs/product/DESIGN_NOTES.md)
    OWNER="UX"; ROLE="UX" ;;
  docs/ux/*)
    OWNER="UX"; ROLE="UX" ;;
  docs/qa/*|reports/*)
    OWNER="QA"; ROLE="QA" ;;
  docs/delivery/*|docker-compose*.yml|docker-compose*.yaml|Dockerfile|*/Dockerfile|.env|.env.*)
    OWNER="Deli (DELIVERY)"; ROLE="DELIVERY" ;;
  memory/PM.md)        OWNER="PM";       ROLE="PM" ;;
  memory/SA.md)        OWNER="SA";       ROLE="SA" ;;
  memory/BA.md)        OWNER="BA";       ROLE="BA" ;;
  memory/UX.md)        OWNER="UX";       ROLE="UX" ;;
  memory/BE.md)        OWNER="BE";       ROLE="BE" ;;
  memory/FE.md)        OWNER="FE";       ROLE="FE" ;;
  memory/QA.md)        OWNER="QA";       ROLE="QA" ;;
  memory/DELIVERY.md)  OWNER="Deli (DELIVERY)"; ROLE="DELIVERY" ;;
  *)
    # Unknown path — allow by default (don't break legitimate edits
    # like CLAUDE.md, new ad-hoc notes, etc.).
    exit 0 ;;
esac

# Log the block for audit.
mkdir -p .pane_logs 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] BLOCKED Orchestrator Write/Edit on $REL_PATH (owner=$OWNER)" \
  >> .pane_logs/_lane_block.log 2>/dev/null || true

cat >&2 <<EOF
================================================================
 BLOCKED — Orchestrator cannot Write/Edit owner-specific files
================================================================
 File:  $REL_PATH
 Owner: $OWNER

 The Orchestrator role is COORDINATOR ONLY. You don't write source
 or owner-specific docs — you route the right agent.

   bash scripts/route_to_pane.sh $ROLE "<task description with the change you want>"

 Allowed Orchestrator files (whitelist):
   TASK.md
   PRODUCT_IDEA.md
   memory/_PROJECT_STATE.md
   memory/ORCHESTRATOR.md

 Audit log:  .pane_logs/_lane_block.log
================================================================
EOF
exit 2
