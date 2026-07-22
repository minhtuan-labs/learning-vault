#!/usr/bin/env bash
# v10.24 — tiny assertion library for the framework's smoke tests.
# No external deps. Each test file sources this, runs assertions, then
# calls `tests_done` which exits non-zero if any assertion failed.

_fail=0
_count=0

_red()   { printf '\033[31m%s\033[0m' "$1"; }
_green() { printf '\033[32m%s\033[0m' "$1"; }

pass() { _count=$((_count+1)); printf '    %s %s\n' "$(_green '[ok]')" "$1"; }
fail() { _count=$((_count+1)); _fail=$((_fail+1)); printf '    %s %s\n' "$(_red '[FAIL]')" "$1"; }

# assert_eq <expected> <actual> <msg>
assert_eq() {
  if [[ "$1" == "$2" ]]; then pass "$3"; else fail "$3 (expected '$1', got '$2')"; fi
}

# assert_contains <haystack> <needle> <msg>
assert_contains() {
  if [[ "$1" == *"$2"* ]]; then pass "$3"; else fail "$3 (missing '$2')"; fi
}

# assert_not_contains <haystack> <needle> <msg>
assert_not_contains() {
  if [[ "$1" != *"$2"* ]]; then pass "$3"; else fail "$3 (unexpectedly found '$2')"; fi
}

# assert_file_contains <file> <grep-ere> <msg>
assert_file_contains() {
  if grep -qE "$2" "$1" 2>/dev/null; then pass "$3"; else fail "$3 (/$2/ not in $1)"; fi
}

# assert_exit <expected_code> <actual_code> <msg>
assert_exit() {
  if [[ "$1" == "$2" ]]; then pass "$3"; else fail "$3 (expected exit $1, got $2)"; fi
}

tests_done() {
  echo "    ---- ${_count} assertion(s), ${_fail} failed ----"
  [[ "$_fail" -eq 0 ]]
}
