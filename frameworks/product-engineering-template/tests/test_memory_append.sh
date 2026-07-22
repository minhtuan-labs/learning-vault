#!/usr/bin/env bash
# v10.24 — tests for scripts/memory_append.sh (locking / no lost writes)
source "$REPO_ROOT/tests/lib.sh"

mkdir -p memory

# --- basic append ---
out=$(bash scripts/memory_append.sh PM "first entry" "hello body"); rc=$?
assert_exit 0 "$rc" "basic append exits 0"
assert_file_contains memory/PM.md "^### .* — first entry" "entry heading written"
assert_file_contains memory/PM.md "hello body" "entry body written"

# --- stdin body ---
echo "piped body content" | bash scripts/memory_append.sh PM "stdin entry" >/dev/null
assert_file_contains memory/PM.md "piped body content" "stdin body written"

# --- bare-stem target (_PROJECT_STATE) ---
bash scripts/memory_append.sh _PROJECT_STATE "state note" "phase moved" >/dev/null
assert_file_contains memory/_PROJECT_STATE.md "state note" "_PROJECT_STATE stem resolves to file"

# --- concurrency: 30 parallel appends, expect exactly 30 intact entries ---
rm -f memory/SA.md
for i in $(seq 1 30); do
  bash scripts/memory_append.sh SA "parallel-$i" "body line for $i" &
done
wait
got=$(grep -c '^### .* — parallel-' memory/SA.md)
assert_eq 30 "$got" "all 30 concurrent appends landed (no lost writes)"
# every entry heading must be on its own line (no interleaving merged two headings)
merged=$(grep -c '### .*### ' memory/SA.md || true)
assert_eq 0 "$merged" "no interleaved/merged heading lines"
# lock dir cleaned up
[[ -d memory/SA.lock.d ]] && leftover=1 || leftover=0
assert_eq 0 "$leftover" "lock dir cleaned up after appends"

tests_done
