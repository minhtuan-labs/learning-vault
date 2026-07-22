#!/usr/bin/env bash
# v10.24 — tests for scripts/check_doc_schema.sh
source "$REPO_ROOT/tests/lib.sh"

mkdir -p docs/product docs/business docs/architecture

# --- incomplete PRD (headings only, no metrics/scope) -> exit 1 ---
cat > docs/product/PRD.md <<'EOF'
# PRD
## Problem
Users struggle.
## Personas
A user.
EOF
out=$(bash scripts/check_doc_schema.sh --file docs/product/PRD.md 2>&1); rc=$?
assert_exit 1 "$rc" "incomplete PRD fails schema"
assert_contains "$out" "[MISS]" "incomplete PRD reports a missing requirement"
assert_contains "$out" "Success metrics" "PRD flags missing success metrics"

# --- complete PRD -> exit 0 ---
cat > docs/product/PRD.md <<'EOF'
# PRD
## Problem statement
Users feel pain doing X.
## Target users / personas
The primary persona is a busy admin.
## Goals / objectives
Goal: reduce time spent.
## Scope / MVP
MVP includes the must-have flows; out of scope: reporting.
## Success metrics
KPI: weekly active users; success metric: task completion rate.
EOF
out=$(bash scripts/check_doc_schema.sh --file docs/product/PRD.md 2>&1); rc=$?
assert_exit 0 "$rc" "complete PRD passes schema"
assert_contains "$out" "-> OK" "complete PRD marked OK"

# --- TECH_STACK without 'Confirmed by user' fails the v10.7 marker ---
cat > docs/architecture/TECH_STACK.md <<'EOF'
# Tech Stack
Frontend: React. Backend: FastAPI. Database: Postgres.
EOF
out=$(bash scripts/check_doc_schema.sh --file docs/architecture/TECH_STACK.md 2>&1); rc=$?
assert_exit 1 "$rc" "unsigned TECH_STACK fails"
assert_contains "$out" "User confirmation" "TECH_STACK flags missing confirmation"

# --- absent doc, not required -> exit 0 ---
out=$(bash scripts/check_doc_schema.sh --file docs/business/USER_STORIES.md 2>&1); rc=$?
assert_exit 0 "$rc" "absent doc skipped when not required"

# --- absent doc, required -> exit 1 ---
out=$(bash scripts/check_doc_schema.sh --require-present 0_DISCOVERY 2>&1); rc=$?
assert_exit 1 "$rc" "--require-present fails on missing required doc"

tests_done
