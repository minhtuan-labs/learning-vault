#!/usr/bin/env bash
# v10.24 — tests for scripts/request_peer_review.sh guard logic.
# (The success path routes to a real tmux pane, which needs a live
#  session; here we verify the validation/guard branches only.)
source "$REPO_ROOT/tests/lib.sh"

mkdir -p docs/product docs/architecture

# --- missing doc -> exit 1 ---
out=$(bash scripts/request_peer_review.sh docs/product/NOPE.md SA 2>&1); rc=$?
assert_exit 1 "$rc" "missing doc rejected"
assert_contains "$out" "not found" "missing doc message"

# --- author cannot review own doc (SA owns architecture) ---
echo "# arch" > docs/architecture/SOLUTION_ARCHITECTURE.md
out=$(bash scripts/request_peer_review.sh docs/architecture/SOLUTION_ARCHITECTURE.md SA 2>&1); rc=$?
assert_exit 1 "$rc" "self-review rejected"
assert_contains "$out" "cannot peer-review its own" "self-review message"

# --- invalid reviewer role -> exit 1 ---
echo "# prd" > docs/product/PRD.md
out=$(bash scripts/request_peer_review.sh docs/product/PRD.md NOTAROLE 2>&1); rc=$?
assert_exit 1 "$rc" "invalid reviewer rejected"
assert_contains "$out" "invalid reviewer" "invalid reviewer message"

# --- no args -> usage exit 2 ---
out=$(bash scripts/request_peer_review.sh 2>&1); rc=$?
assert_exit 2 "$rc" "no args -> usage error"

tests_done
