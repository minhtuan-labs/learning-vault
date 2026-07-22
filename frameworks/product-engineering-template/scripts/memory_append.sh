#!/usr/bin/env bash
set -euo pipefail

# v10.24 — Atomic, locked append to a memory file.
#
# WHY: when the Orchestrator fans a phase out to several panes in
# parallel (e.g. discovery -> PM + BA + UX, or two tasks routed to the
# same role back-to-back, or the watcher_daemon auto-resuming a worker
# while another task runs), multiple processes can append to a memory/
# file at nearly the same instant. Plain `>>` from two writers can
# interleave bytes and corrupt an entry. This helper serializes writes
# with a mutex so each entry lands whole.
#
# Portable locking: uses flock(1) when present (Linux), otherwise falls
# back to an atomic `mkdir` mutex (works on macOS bash 3.2, no deps).
#
# Usage:
#   bash scripts/memory_append.sh <ROLE> "<title>" "<body...>"
#   bash scripts/memory_append.sh <ROLE> "<title>" < body_from_stdin
#   echo "free text" | bash scripts/memory_append.sh _PROJECT_STATE "<title>"
#
# <ROLE> may be a role name (PM, SA, ... -> memory/<ROLE>.md) or a bare
# file stem like _PROJECT_STATE (-> memory/_PROJECT_STATE.md). A full
# path ending in .md is also accepted.
#
# The entry is written in the standard format the framework expects:
#   ### YYYY-MM-DD HH:MM — <title>
#   <body>
#
# Exit codes: 0 ok, 1 lock timeout, 2 usage error.

ROLE="${1:-}"
TITLE="${2:-}"
if [[ -z "$ROLE" || -z "$TITLE" ]]; then
  echo "Usage: bash scripts/memory_append.sh <ROLE> \"<title>\" [\"<body>\"]" >&2
  echo "       (body may also be supplied on stdin)" >&2
  exit 2
fi
shift 2 || true

# Resolve the target file.
case "$ROLE" in
  *.md) FILE="$ROLE" ;;
  memory/*) FILE="${ROLE}.md" ;;
  *) FILE="memory/${ROLE}.md" ;;
esac
mkdir -p "$(dirname "$FILE")"

# Gather body: remaining args win; otherwise read stdin if piped.
BODY=""
if (( $# > 0 )); then
  BODY="$*"
elif [[ ! -t 0 ]]; then
  BODY="$(cat)"
fi
[[ -z "$BODY" ]] && BODY="(no detail)"

STAMP="$(date '+%Y-%m-%d %H:%M')"
ENTRY="$(printf '\n### %s — %s\n%s\n' "$STAMP" "$TITLE" "$BODY")"

LOCKDIR="${FILE%.md}.lock.d"
LOCKFLOCK="${FILE%.md}.lock"
TIMEOUT="${MEMORY_LOCK_TIMEOUT:-15}"

do_append() {
  # Ensure the file exists with a header if brand-new.
  if [[ ! -f "$FILE" ]]; then
    printf '# Memory — %s\n' "$(basename "${FILE%.md}")" > "$FILE"
  fi
  printf '%s\n' "$ENTRY" >> "$FILE"
}

if command -v flock >/dev/null 2>&1; then
  # Linux fast path: flock on a dedicated lock file.
  exec 9>"$LOCKFLOCK"
  if ! flock -w "$TIMEOUT" 9; then
    echo "memory_append: lock timeout on $FILE" >&2
    exit 1
  fi
  do_append
  # lock released when fd 9 closes on exit
else
  # Portable mutex: mkdir is atomic on POSIX filesystems.
  waited=0
  until mkdir "$LOCKDIR" 2>/dev/null; do
    sleep 0.2
    waited=$(awk -v w="$waited" 'BEGIN{printf "%.1f", w+0.2}')
    if awk -v w="$waited" -v t="$TIMEOUT" 'BEGIN{exit !(w>=t)}'; then
      echo "memory_append: lock timeout on $FILE (held by another writer?)" >&2
      echo "  If stale, remove: $LOCKDIR" >&2
      exit 1
    fi
  done
  trap 'rmdir "$LOCKDIR" 2>/dev/null || true' EXIT
  do_append
  rmdir "$LOCKDIR" 2>/dev/null || true
  trap - EXIT
fi

echo "memory_append: appended to $FILE"
