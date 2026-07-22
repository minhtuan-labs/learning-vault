#!/usr/bin/env bash
set -euo pipefail

# v10.24 — Compact append-only memory files.
#
# WHY: memory/<ROLE>.md is append-only (see memory/README.md). Over a
# long project it grows without bound, which quietly defeats the v10.6
# goal of keeping per-task reads small/cheap — every worker re-reads its
# whole memory file at the start of every task. This script keeps the
# most recent entries in place and ARCHIVES older ones to
# memory/archive/, so the live file stays lean while nothing is lost.
#
# Strategy is deterministic (no LLM call, works offline, same result
# every time): an "entry" is a block starting at a `### ` heading. The
# file header (everything before the first `### `) is always preserved.
# The newest KEEP_RECENT entries stay; older entries are moved to
# memory/archive/<base>.<timestamp>.md and replaced with a one-line
# pointer.
#
# Usage:
#   bash scripts/compact_memory.sh [--keep N] [--dry-run] [--force] [files...]
#
#   --keep N    keep the newest N entries in place (default 12)
#   --dry-run   show what would happen, change nothing
#   --force     compact even if a file is under the trigger size
#   files...    specific memory files; default = memory/<ROLE>.md for the
#               9 roles + _PROJECT_STATE.md
#
# A file is only compacted if it has MORE than KEEP_RECENT entries AND
# (its size >= TRIGGER_BYTES OR --force). TRIGGER_BYTES default 8000.
#
# Exit codes: 0 ok, 2 usage error.

KEEP="${MEMORY_KEEP_RECENT:-12}"
TRIGGER="${MEMORY_COMPACT_TRIGGER_BYTES:-8000}"
DRY=false
FORCE=false
FILES=()

while (( $# > 0 )); do
  case "$1" in
    --keep)    KEEP="${2:-}"; shift 2 ;;
    --dry-run) DRY=true; shift ;;
    --force)   FORCE=true; shift ;;
    -h|--help) grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "Unknown flag: $1" >&2; exit 2 ;;
    *)  FILES+=("$1"); shift ;;
  esac
done

if ! [[ "$KEEP" =~ ^[0-9]+$ ]]; then
  echo "--keep must be a non-negative integer (got: $KEEP)" >&2
  exit 2
fi

if (( ${#FILES[@]} == 0 )); then
  for r in ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY _PROJECT_STATE; do
    [[ -f "memory/${r}.md" ]] && FILES+=("memory/${r}.md")
  done
fi

if (( ${#FILES[@]} == 0 )); then
  echo "No memory files found. Run from the project root."
  exit 0
fi

ARCHIVE_DIR="memory/archive"
NOW_TS="$(date '+%Y%m%d-%H%M%S')"
NOW_HUMAN="$(date '+%Y-%m-%d %H:%M')"
total_archived=0

for FILE in "${FILES[@]}"; do
  [[ -f "$FILE" ]] || { echo "skip (missing): $FILE"; continue; }

  entry_count=$(grep -c '^### ' "$FILE" 2>/dev/null || echo 0)
  size=$(wc -c < "$FILE" 2>/dev/null | tr -d ' ')

  if (( entry_count <= KEEP )); then
    echo "skip: $FILE — ${entry_count} entr(ies) <= keep ${KEEP}"
    continue
  fi
  if (( size < TRIGGER )) && ! $FORCE; then
    echo "skip: $FILE — ${size}B < trigger ${TRIGGER}B (use --force to override)"
    continue
  fi

  # Line numbers of all entry headings (portable; no bash-4 mapfile).
  starts=()
  while IFS= read -r ln; do starts+=("$ln"); done < <(grep -n '^### ' "$FILE" | cut -d: -f1)
  first_entry_line="${starts[0]}"
  # The first entry we KEEP is index (entry_count - KEEP) in 0-based starts.
  keep_from_idx=$(( entry_count - KEEP ))
  cutoff_line="${starts[$keep_from_idx]}"

  archive_to_move=$(( entry_count - KEEP ))

  if $DRY; then
    echo "would compact: $FILE — keep ${KEEP}, archive ${archive_to_move} older entr(ies) (size ${size}B)"
    continue
  fi

  mkdir -p "$ARCHIVE_DIR"
  base="$(basename "${FILE%.md}")"
  ARCHIVE_FILE="${ARCHIVE_DIR}/${base}.${NOW_TS}.md"

  # 1) Archived entries = from first entry line .. (cutoff_line - 1)
  {
    echo "# Archived memory entries — ${base}"
    echo "# Compacted ${NOW_HUMAN}. These are older entries moved out of"
    echo "# ${FILE} to keep the live file lean. Newest entries stay in place."
    echo
    sed -n "${first_entry_line},$(( cutoff_line - 1 ))p" "$FILE"
  } > "$ARCHIVE_FILE"

  # 2) New live file = header (1..first_entry_line-1) + pointer + kept entries
  tmp="$(mktemp)"
  {
    if (( first_entry_line > 1 )); then
      sed -n "1,$(( first_entry_line - 1 ))p" "$FILE"
    fi
    echo
    echo "> _Compacted ${NOW_HUMAN}: ${archive_to_move} older entr(ies) archived to_"
    echo "> _\`${ARCHIVE_FILE}\`. Newest ${KEEP} kept below._"
    echo
    sed -n "${cutoff_line},\$p" "$FILE"
  } > "$tmp"
  mv "$tmp" "$FILE"

  total_archived=$(( total_archived + archive_to_move ))
  new_size=$(wc -c < "$FILE" | tr -d ' ')
  echo "compacted: $FILE — archived ${archive_to_move} entr(ies) -> ${ARCHIVE_FILE} (size ${size}B -> ${new_size}B)"
done

echo "----------------------------------------------------------------"
if $DRY; then
  echo "Dry run — no files changed."
else
  echo "Done. Archived ${total_archived} entr(ies) total into ${ARCHIVE_DIR}/."
fi
