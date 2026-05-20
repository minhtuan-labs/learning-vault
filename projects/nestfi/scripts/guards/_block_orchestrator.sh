#!/usr/bin/env bash
# v10.19 — Hard guard for the Orchestrator pane.
#
# How it works:
#   - start_agents_tmux.sh prepends this directory to the Orchestrator
#     pane's PATH (and ONLY the Orchestrator pane's).
#   - Each forbidden command (docker, psql, python, npm, ...) has a
#     wrapper script in this dir that exec's THIS script.
#   - When the Orchestrator tries to run a forbidden command, the
#     wrapper fires, prints a clear "route to <role>" message to stderr,
#     and exits non-zero.
#   - Worker panes (BE/FE/QA/DELIVERY/etc.) do NOT have this dir in
#     PATH, so their real binaries are used as normal.
#
# This is hard enforcement: the model cannot accidentally run
# engineering commands in the Orchestrator pane even if its prompt
# rule slips. Multi-model specialization stays intact.
#
# Bypass: a model that genuinely needs to invoke the real binary can
# use `command <cmd>` or `/path/to/<cmd>` (both bypass PATH lookup).
# That's intentional — bypass requires explicit, auditable intent
# rather than accidental fall-through.

CMD="${1:-unknown}"
shift 2>/dev/null || true

# v10.19 — log every block attempt so audit / debug can see what was tried.
GUARD_LOG="${TMPDIR:-/tmp}/orchestrator_guard.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] BLOCKED $CMD $*" >> "$GUARD_LOG" 2>/dev/null || true

case "$CMD" in
  docker|docker-compose|podman|kubectl|helm|colima|minikube)
    OWNER="DELIVERY" ; CATEGORY="container/k8s operations" ;;
  psql|mongo|mongosh|redis-cli|mysql|sqlite3|pg_dump|mongorestore)
    OWNER="BE" ; CATEGORY="database CLI" ;;
  alembic|prisma|sequelize-cli|knex|flask-migrate)
    OWNER="BE" ; CATEGORY="database migration tooling" ;;
  python|python3|node|deno|bun|ruby|java|go)
    OWNER="BE or FE (depending on what the script is for)"
    CATEGORY="language runtime" ;;
  pip|pip3|pipx|poetry|conda)
    OWNER="BE" ; CATEGORY="Python package manager" ;;
  npm|yarn|pnpm|npx)
    OWNER="FE (or BE if Node backend)" ; CATEGORY="Node package manager" ;;
  cargo|gem|bundle|mvn|gradle)
    OWNER="BE or FE" ; CATEGORY="build/package manager" ;;
  curl|wget|httpie)
    OWNER="QA (for testing the running app)"
    CATEGORY="HTTP client (against running app)"
    # Note: curl is technically allowed for Orchestrator to read
    # web URLs, but most uses against localhost are app-testing.
    # We block by default and tell the model to route QA.
    ;;
  *)
    OWNER="appropriate role per Stay-in-Lane table"
    CATEGORY="engineering action" ;;
esac

cat >&2 <<EOF
================================================================
 BLOCKED — Orchestrator cannot execute engineering commands
================================================================
 Command:  $CMD
 Category: $CATEGORY
 Owner:    $OWNER

 This command is part of $OWNER's lane. The Orchestrator role is
 COORDINATOR ONLY — you delegate, you do not execute. Running
 engineering commands directly bypasses the multi-model
 specialization the framework is built on.

 Route to $OWNER instead. Example:

   bash scripts/route_to_pane.sh ${OWNER%% *} \\
     "<the work that needed $CMD, described as a task>"

 If this command is genuinely required for orchestration (rare),
 bypass the guard with:    command $CMD ...     (or absolute path)
 — but consider this a code smell and file a framework issue.
================================================================
EOF
exit 126
