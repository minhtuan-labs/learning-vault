#!/usr/bin/env bash
set -uo pipefail

# v10.24 — Framework smoke-test runner.
#
# The version history (v10.12.1 auto-wake regression, v10.18.1 pane
# detection) shows that script edits have repeatedly broken the
# framework in ways nobody caught until a live session failed. This
# runner gives a fast, dependency-free safety net:
#
#   PHASE 1  syntax — `bash -n` on every shell script in scripts/ + tests/
#   PHASE 2  behaviour — each tests/test_*.sh runs in an isolated sandbox
#            (a temp dir seeded with scripts/ + config/) so tests never
#            touch the real project tree.
#
# Usage:  bash tests/run_tests.sh
# Exit:   0 all green, 1 any failure.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

fail_total=0

echo "================================================================"
echo " PHASE 1 — syntax check (bash -n)"
echo "================================================================"
syntax_fail=0
while IFS= read -r f; do
  if bash -n "$f" 2>/tmp/_synerr; then
    printf "  [ok]   %s\n" "$f"
  else
    printf "  [FAIL] %s\n" "$f"
    sed 's/^/         /' /tmp/_synerr
    syntax_fail=$((syntax_fail+1))
  fi
done < <(find scripts tests -name '*.sh' -type f | sort)
rm -f /tmp/_synerr
if (( syntax_fail > 0 )); then
  echo "  -> ${syntax_fail} script(s) failed syntax check"
  fail_total=$((fail_total+syntax_fail))
else
  echo "  -> all scripts parse cleanly"
fi

echo
echo "================================================================"
echo " PHASE 2 — behaviour tests (sandboxed)"
echo "================================================================"

seed_sandbox() {  # $1 = sandbox dir
  local sb="$1"
  mkdir -p "$sb"
  cp -R "$REPO_ROOT/scripts" "$sb/scripts"
  cp -R "$REPO_ROOT/config"  "$sb/config"
  mkdir -p "$sb/memory" "$sb/docs" "$sb/reports" "$sb/planning"
}

for t in "$REPO_ROOT"/tests/test_*.sh; do
  [[ -e "$t" ]] || continue
  name="$(basename "$t")"
  echo
  echo "--- $name ---"
  sandbox="$(mktemp -d)"
  seed_sandbox "$sandbox"
  if ( cd "$sandbox" && REPO_ROOT="$REPO_ROOT" SANDBOX="$sandbox" bash "$t" ); then
    echo "  => $name PASSED"
  else
    echo "  => $name FAILED"
    fail_total=$((fail_total+1))
  fi
  rm -rf "$sandbox"
done

echo
echo "================================================================"
if (( fail_total == 0 )); then
  echo " ALL TESTS PASSED"
  echo "================================================================"
  exit 0
else
  echo " ${fail_total} FAILURE(S)"
  echo "================================================================"
  exit 1
fi
