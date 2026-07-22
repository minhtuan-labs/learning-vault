#!/usr/bin/env bash
# v10.24 — tests for scripts/cost_report.sh  (runs in a sandbox cwd)
source "$REPO_ROOT/tests/lib.sh"

mkdir -p .pane_logs .pane_tasks memory

# --- no receipts -> friendly exit 0 ---
out=$(bash scripts/cost_report.sh 2>&1); rc=$?
assert_exit 0 "$rc" "no-data run exits 0"
assert_contains "$out" "No routing receipts" "no-data run prints friendly message"

# --- fabricate two runs: SA/opus and PM/haiku ---
cat > .pane_logs/_routing_receipts.log <<'EOF'
[2026-05-20 10:00:00] route_to_pane.sh -> SA (pane=%3, model=claude-opus-4-6)
  task_file=.pane_tasks/SA_20260520_100000.md
  log_file=.pane_logs/SA_20260520_100000.log
  message=design the architecture
[2026-05-20 11:00:00] route_to_pane.sh -> PM (pane=%1, model=claude-haiku-4-5)
  task_file=.pane_tasks/PM_20260520_110000.md
  log_file=.pane_logs/PM_20260520_110000.log
  message=write the PRD
EOF

# known sizes: 4000-char input, 8000-char output each
head -c 4000 /dev/zero | tr '\0' 'x' > .pane_tasks/SA_20260520_100000.md
head -c 8000 /dev/zero | tr '\0' 'y' > .pane_logs/SA_20260520_100000.log
head -c 4000 /dev/zero | tr '\0' 'x' > .pane_tasks/PM_20260520_110000.md
head -c 8000 /dev/zero | tr '\0' 'y' > .pane_logs/PM_20260520_110000.log

# phase timeline so attribution is exercised
cat > memory/_PROJECT_STATE.md <<'EOF'
## Session log
- 2026-05-20 09:00:00 — advanced to 1_SOLUTION_DESIGN
EOF

# --- JSON mode ---
json=$(bash scripts/cost_report.sh --json 2>&1); rc=$?
assert_exit 0 "$rc" "--json exits 0"
assert_contains "$json" '"role":"SA"' "json has SA run"
assert_contains "$json" '"role":"PM"' "json has PM run"
assert_contains "$json" '"model":"claude-opus-4-6"' "json records opus model"
assert_contains "$json" '"phase":"1_SOLUTION_DESIGN"' "json attributes phase from state log"
# SA opus: in=1000tok*15/1e6 + out=2000tok*75/1e6 = 0.015 + 0.15 = 0.165
assert_contains "$json" '"cost_usd":0.165000' "SA opus run cost computed correctly"
# total = 0.165 (SA) + (0.001 + 0.01 = 0.011 PM) = 0.176
assert_contains "$json" '"total_cost_usd":0.176000' "total cost summed correctly"

# --- summary + by-run modes ---
sumr=$(bash scripts/cost_report.sh 2>&1); rc=$?
assert_exit 0 "$rc" "summary exits 0"
assert_contains "$sumr" "By role" "summary groups by role"
assert_contains "$sumr" "By phase" "summary groups by phase"
assert_contains "$sumr" "TOTAL" "summary prints total"

byrun=$(bash scripts/cost_report.sh --by-run 2>&1)
assert_contains "$byrun" "By run" "by-run lists individual runs"

tests_done
