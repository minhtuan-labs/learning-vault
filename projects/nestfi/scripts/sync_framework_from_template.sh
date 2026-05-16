#!/usr/bin/env bash
set -euo pipefail

# v10.11 — Safely sync FRAMEWORK files from a newer template into an
# active project, without touching any of the team's work outputs.
#
# Usage (run from the project root):
#   bash scripts/sync_framework_from_template.sh <TEMPLATE_PATH>
#   bash scripts/sync_framework_from_template.sh <TEMPLATE_PATH> --dry-run
#
# What it copies (framework-owned, safe to overwrite):
#   AGENTS.md  README.md  VERSION.md  LICENSE  .gitignore
#   PRODUCT_ENGINEERING.md
#   .opencode/config.json  opencode.json
#   scripts/*.sh
#   prompts/agents/*.md
#   config/*
#   planning/PANE_ROUTING_RULES.md
#   planning/ORCHESTRATOR_RUNTIME_RULES.md
#   planning/AGENT_WORKFLOW.md
#   docs/delivery/OPENCODE_SETUP.md
#   docs/delivery/TMUX_USAGE.md
#   memory/README.md
#
# What it NEVER touches (project-owned — the team's work):
#   PRODUCT_IDEA.md  TASK.md
#   memory/_PROJECT_STATE.md  memory/<ROLE>.md (the non-README ones)
#   docs/product/{PRD,ROADMAP,UX_FLOW,WIREFRAMES,DESIGN_NOTES}.md
#   docs/business/{BUSINESS_REQUIREMENTS,USER_STORIES,DOMAIN_MODEL}.md
#   docs/architecture/{SOLUTION_ARCHITECTURE,TECH_STACK,ADR,API_CONTRACT}.md
#   docs/qa/{TEST_PLAN,TEST_CASES}.md
#   docs/delivery/{DELIVERY_PLAN,RELEASE_NOTES,RUNNING_APP}.md
#   planning/{BACKLOG,OPEN_QUESTIONS,BE_PLAN,FE_PLAN}.md
#   reports/{TEST_REPORT,BUG_REPORT}.md
#   backend/*  frontend/*
#   .pane_* / .agent_* (runtime)
#
# Backup: each file overwritten is backed up to .framework_sync_backup/
# under the same relative path, with timestamp suffix.

TEMPLATE="${1:-}"
DRY_RUN=false
if [[ "${2:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

if [[ -z "$TEMPLATE" ]]; then
  echo "Usage: bash scripts/sync_framework_from_template.sh <TEMPLATE_PATH> [--dry-run]"
  exit 2
fi

if [[ ! -d "$TEMPLATE" ]]; then
  echo "ERROR: template path does not exist or is not a directory: $TEMPLATE"
  exit 2
fi

# Sanity-check that the template looks like the right thing
for sentinel in AGENTS.md VERSION.md scripts/route_to_pane.sh prompts/agents/ORCHESTRATOR.md; do
  if [[ ! -f "$TEMPLATE/$sentinel" ]]; then
    echo "ERROR: $TEMPLATE does not look like a product-engineering-template (missing $sentinel)"
    exit 2
  fi
done

PROJECT="$(pwd)"
if [[ "$TEMPLATE" -ef "$PROJECT" ]]; then
  echo "ERROR: refusing to sync a directory into itself."
  exit 2
fi

# The exact list of framework-owned files. Globs are expanded against
# the TEMPLATE.
FRAMEWORK_PATHS=(
  "AGENTS.md"
  "CLAUDE.md"
  "README.md"
  "VERSION.md"
  "LICENSE"
  ".gitignore"
  "PRODUCT_ENGINEERING.md"
  ".opencode/config.json"
  "opencode.json"
  "memory/README.md"
  "planning/PANE_ROUTING_RULES.md"
  "planning/ORCHESTRATOR_RUNTIME_RULES.md"
  "planning/AGENT_WORKFLOW.md"
  "docs/delivery/OPENCODE_SETUP.md"
  "docs/delivery/TMUX_USAGE.md"
)
FRAMEWORK_GLOBS=(
  "scripts/*.sh"
  "prompts/agents/*.md"
  "config/*"                       # top-level config files
  "config/engines/*"               # v10.12 — engine env files + README
)

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR=".framework_sync_backup/$TS"

copy_one() {
  local rel="$1"
  local src="$TEMPLATE/$rel"
  local dst="$PROJECT/$rel"
  if [[ ! -f "$src" ]]; then
    return 0   # silently skip missing template entries
  fi
  if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then
    echo "    = $rel (unchanged)"
    return 0
  fi
  if [[ -f "$dst" ]]; then
    if ! $DRY_RUN; then
      mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
      cp "$dst" "$BACKUP_DIR/$rel"
    fi
    echo "    ~ $rel (overwrite; backup → $BACKUP_DIR/$rel)"
  else
    echo "    + $rel (new file)"
  fi
  if ! $DRY_RUN; then
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    # preserve executable bit for scripts
    if [[ "$rel" == scripts/*.sh ]]; then
      chmod +x "$dst"
    fi
  fi
}

echo "================================================================"
echo " Framework sync from template"
echo "   template: $TEMPLATE"
echo "   project : $PROJECT"
echo "   mode    : $([ $DRY_RUN = true ] && echo DRY-RUN || echo APPLY)"
echo " Backups (if any) → $BACKUP_DIR/"
echo "================================================================"

echo
echo "[framework-owned, fixed list]"
for p in "${FRAMEWORK_PATHS[@]}"; do
  copy_one "$p"
done

echo
echo "[framework-owned, glob-expanded]"
for g in "${FRAMEWORK_GLOBS[@]}"; do
  # Expand glob inside the template dir
  pushd "$TEMPLATE" >/dev/null
  shopt -s nullglob
  matches=( $g )
  shopt -u nullglob
  popd >/dev/null
  if (( ${#matches[@]} == 0 )); then
    echo "    (no matches for $g)"
    continue
  fi
  for m in "${matches[@]}"; do
    copy_one "$m"
  done
done

echo
echo "================================================================"
echo " Project-owned files NEVER touched by this sync:"
echo "   PRODUCT_IDEA.md, TASK.md"
echo "   memory/<ROLE>.md, memory/_PROJECT_STATE.md"
echo "   docs/product/*.md, docs/business/*.md, docs/architecture/*.md"
echo "   docs/qa/*.md, docs/delivery/{DELIVERY_PLAN,RELEASE_NOTES,RUNNING_APP}.md"
echo "   planning/{BACKLOG,OPEN_QUESTIONS,BE_PLAN,FE_PLAN}.md"
echo "   reports/*.md, backend/*, frontend/*"
echo "================================================================"

if $DRY_RUN; then
  echo "DRY-RUN complete — no files were changed."
else
  echo "Sync complete. If anything looks wrong, restore from $BACKUP_DIR/."
fi
