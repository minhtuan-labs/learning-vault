#!/usr/bin/env bash
# v10.24 — tests for scripts/compact_memory.sh
source "$REPO_ROOT/tests/lib.sh"

mkdir -p memory

# Build a memory file with a header + 20 dated entries.
{
  echo "# Memory — PM"
  echo
  echo "## Decisions"
  for i in $(seq 1 20); do
    printf '\n### 2026-05-%02d 10:00 — entry %d\nbody for entry %d\n' "$i" "$i" "$i"
  done
} > memory/PM.md

before=$(grep -c '^### ' memory/PM.md)
assert_eq 20 "$before" "fixture has 20 entries"

# --- dry run changes nothing ---
out=$(bash scripts/compact_memory.sh --keep 5 --force --dry-run memory/PM.md 2>&1)
assert_contains "$out" "would compact" "dry-run announces intent"
still=$(grep -c '^### ' memory/PM.md)
assert_eq 20 "$still" "dry-run leaves file untouched"

# --- real compaction: keep 5 ---
bash scripts/compact_memory.sh --keep 5 --force memory/PM.md >/dev/null
kept=$(grep -c '^### ' memory/PM.md)
assert_eq 5 "$kept" "live file keeps newest 5 entries"
assert_file_contains memory/PM.md "entry 20" "newest entry retained"
assert_file_contains memory/PM.md "^# Memory — PM" "file header preserved"
assert_file_contains memory/PM.md "Compacted" "pointer note inserted"

arch=$(ls memory/archive/PM.*.md 2>/dev/null | head -1)
[[ -n "$arch" ]] && have_arch=1 || have_arch=0
assert_eq 1 "$have_arch" "archive file created"
archived=$(grep -c '^### ' "$arch")
assert_eq 15 "$archived" "archive holds the 15 older entries"
assert_file_contains "$arch" "entry 1" "oldest entry moved to archive"

# --- under-threshold file is skipped without --force ---
printf '# Memory — QA\n\n### 2026-05-01 10:00 — a\nx\n### 2026-05-02 10:00 — b\ny\n' > memory/QA.md
out2=$(bash scripts/compact_memory.sh --keep 1 memory/QA.md 2>&1)
assert_contains "$out2" "skip" "small file skipped without --force"

tests_done
