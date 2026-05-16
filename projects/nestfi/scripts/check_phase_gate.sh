#!/usr/bin/env bash
set -euo pipefail

# v10.9 — Phase completion gate.
#
# Asks: "Is phase <N> complete enough that we can move on?" Each phase
# has a set of required output files (with substantive content) plus
# zero or more semantic checks (e.g. TECH_STACK.md must say
# "Confirmed by user", TEST_REPORT.md must start with VERDICT: PASS,
# BUG_REPORT.md must have no OPEN_CRITICAL/OPEN_MAJOR).
#
# Usage:
#   bash scripts/check_phase_gate.sh <PHASE>
#   bash scripts/check_phase_gate.sh --through <PHASE>
#
# PHASE is one of:
#   0_DISCOVERY  1_SOLUTION_DESIGN  2_BACKLOG_AND_SPEC
#   3_IMPLEMENTATION_PLANNING  4_BUILD  5_TEST_AND_FIX  6_DELIVERY
#
# Exit codes:
#   0  — phase complete (or in --through, every listed phase complete)
#   1  — phase incomplete (missing outputs / failed semantic check)
#   2  — usage error

THROUGH=false
if [[ "${1:-}" == "--through" ]]; then
  THROUGH=true
  shift
fi

PHASE="${1:-}"
if [[ -z "$PHASE" ]]; then
  echo "Usage: bash scripts/check_phase_gate.sh [--through] <PHASE>"
  echo "Phases: 0_DISCOVERY 1_SOLUTION_DESIGN 2_BACKLOG_AND_SPEC"
  echo "        3_IMPLEMENTATION_PLANNING 4_BUILD 5_TEST_AND_FIX 6_DELIVERY"
  exit 2
fi

THRESHOLD="${PHASE_GATE_THRESHOLD:-200}"

ALL_PHASES=(
  "0_DISCOVERY"
  "1_SOLUTION_DESIGN"
  "2_BACKLOG_AND_SPEC"
  "3_IMPLEMENTATION_PLANNING"
  "4_BUILD"
  "5_TEST_AND_FIX"
  "6_DELIVERY"
)

# Phase outputs use both real filenames and synthetic tokens:
#   _CODE_BE_                          — backend/ has source files
#   _CODE_FE_                          — frontend/ has source files
#   _SIGNED_TECH_STACK_                — TECH_STACK.md confirmed by user
#   _VERDICT_PASS_                     — TEST_REPORT.md says PASS
#   _NO_OPEN_CRITICAL_MAJOR_           — BUG_REPORT.md clean
#   _RUNNING_APP_URL_                  — RUNNING_APP.md has a real URL
get_phase_outputs() {
  case "$1" in
    0_DISCOVERY)
      echo "docs/product/PRD.md docs/business/BUSINESS_REQUIREMENTS.md docs/business/USER_STORIES.md docs/product/UX_FLOW.md"
      ;;
    1_SOLUTION_DESIGN)
      echo "docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/architecture/ADR.md docs/architecture/API_CONTRACT.md _SIGNED_TECH_STACK_"
      ;;
    2_BACKLOG_AND_SPEC)
      echo "planning/BACKLOG.md docs/business/USER_STORIES.md"
      ;;
    3_IMPLEMENTATION_PLANNING)
      echo "planning/BE_PLAN.md planning/FE_PLAN.md docs/qa/TEST_PLAN.md docs/qa/TEST_CASES.md docs/delivery/DELIVERY_PLAN.md"
      ;;
    4_BUILD)
      echo "_CODE_BE_ _CODE_FE_"
      ;;
    5_TEST_AND_FIX)
      echo "reports/TEST_REPORT.md _VERDICT_PASS_ _NO_OPEN_CRITICAL_MAJOR_"
      ;;
    6_DELIVERY)
      echo "docker-compose.yml backend/Dockerfile frontend/Dockerfile docs/delivery/RUNNING_APP.md _RUNNING_APP_URL_ docs/delivery/RELEASE_NOTES.md"
      ;;
    *)
      echo ""
      ;;
  esac
}

# Returns 0 if check passes, 1 otherwise. Prints status text.
check_token() {
  local token="$1"
  case "$token" in
    _CODE_BE_)
      local count
      count=$(find backend -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' \) 2>/dev/null | wc -l | tr -d ' ')
      if [[ -n "$count" ]] && (( count > 0 )); then
        echo "OK (${count} source files in backend/)"
        return 0
      fi
      echo "MISSING (no source files in backend/)"
      return 1
      ;;
    _CODE_FE_)
      local count
      count=$(find frontend -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' -o -name '*.astro' -o -name '*.html' \) 2>/dev/null | wc -l | tr -d ' ')
      if [[ -n "$count" ]] && (( count > 0 )); then
        echo "OK (${count} source files in frontend/)"
        return 0
      fi
      echo "MISSING (no source files in frontend/)"
      return 1
      ;;
    _SIGNED_TECH_STACK_)
      if [[ -f docs/architecture/TECH_STACK.md ]] && grep -qi "Confirmed by user" docs/architecture/TECH_STACK.md; then
        echo "OK (TECH_STACK.md has 'Confirmed by user' line)"
        return 0
      fi
      echo "MISSING (TECH_STACK.md lacks 'Confirmed by user' line — SA likely skipped the Tech Stack Confirmation Protocol)"
      return 1
      ;;
    _VERDICT_PASS_)
      if [[ -f reports/TEST_REPORT.md ]]; then
        local first
        first=$(grep -m1 -E '^[A-Za-z]' reports/TEST_REPORT.md 2>/dev/null || true)
        if [[ "$first" =~ ^VERDICT:[[:space:]]*PASS ]]; then
          echo "OK (VERDICT: PASS)"
          return 0
        fi
        echo "MISSING (TEST_REPORT.md first non-blank line is: ${first:-empty} — not VERDICT: PASS)"
        return 1
      fi
      echo "MISSING (no TEST_REPORT.md)"
      return 1
      ;;
    _NO_OPEN_CRITICAL_MAJOR_)
      if [[ ! -f reports/BUG_REPORT.md ]]; then
        echo "OK (no BUG_REPORT.md — assume clean)"
        return 0
      fi
      # Look for Status: OPEN_CRITICAL or OPEN_MAJOR (case insensitive)
      local hits
      hits=$(grep -ciE '^[-*[:space:]]*Status:[[:space:]]*(OPEN_CRITICAL|OPEN_MAJOR|RETEST_FAIL)' reports/BUG_REPORT.md 2>/dev/null || echo 0)
      if [[ -n "$hits" ]] && (( hits > 0 )); then
        echo "MISSING (${hits} bug(s) with OPEN_CRITICAL / OPEN_MAJOR / RETEST_FAIL status in BUG_REPORT.md)"
        return 1
      fi
      echo "OK (no OPEN_CRITICAL / OPEN_MAJOR / RETEST_FAIL bugs)"
      return 0
      ;;
    _RUNNING_APP_URL_)
      if [[ -f docs/delivery/RUNNING_APP.md ]] && grep -qiE 'https?://' docs/delivery/RUNNING_APP.md; then
        local url
        url=$(grep -oE 'https?://[^[:space:]>)"'\'']+' docs/delivery/RUNNING_APP.md | head -1)
        echo "OK (URL found: ${url})"
        return 0
      fi
      echo "MISSING (RUNNING_APP.md has no http(s):// URL — deploy likely not run)"
      return 1
      ;;
    *)
      # Plain file path check
      if [[ -f "$token" ]]; then
        local sz
        sz=$(wc -c < "$token" 2>/dev/null | tr -d ' ')
        if [[ -n "$sz" ]] && (( sz >= THRESHOLD )); then
          echo "OK (${sz}B)"
          return 0
        fi
        echo "SKELETON (${sz:-0}B < ${THRESHOLD}B)"
        return 1
      fi
      echo "MISSING (file not found)"
      return 1
      ;;
  esac
}

check_one_phase() {
  local phase="$1"
  local outputs
  outputs="$(get_phase_outputs "$phase")"
  if [[ -z "$outputs" ]]; then
    echo "Unknown phase: $phase"
    return 2
  fi

  local fail_count=0
  echo "--- Phase $phase ---"
  for tok in $outputs; do
    local status
    if status=$(check_token "$tok"); then
      printf "  %-45s  %s\n" "$tok" "$status"
    else
      printf "  %-45s  %s\n" "$tok" "$status"
      fail_count=$((fail_count + 1))
    fi
  done
  if (( fail_count == 0 )); then
    echo "  → Phase $phase: COMPLETE"
    return 0
  else
    echo "  → Phase $phase: INCOMPLETE (${fail_count} item(s) missing)"
    return 1
  fi
}

# Validate phase name
phase_known=false
for p in "${ALL_PHASES[@]}"; do
  if [[ "$p" == "$PHASE" ]]; then
    phase_known=true
    break
  fi
done
if ! $phase_known; then
  echo "Unknown phase: $PHASE"
  echo "Phases: ${ALL_PHASES[*]}"
  exit 2
fi

echo "================================================================"
if $THROUGH; then
  echo " Phase gate check — through ${PHASE}"
else
  echo " Phase gate check — ${PHASE}"
fi
echo " (substantive content threshold: ${THRESHOLD} bytes)"
echo "================================================================"

overall_rc=0

if $THROUGH; then
  for p in "${ALL_PHASES[@]}"; do
    check_one_phase "$p" || overall_rc=1
    echo
    if [[ "$p" == "$PHASE" ]]; then
      break
    fi
  done
else
  check_one_phase "$PHASE" || overall_rc=1
fi

echo "================================================================"
if (( overall_rc == 0 )); then
  if $THROUGH; then
    echo " All phases 0 through ${PHASE} are COMPLETE."
  else
    echo " Phase ${PHASE} is COMPLETE."
  fi
else
  echo " GATE FAILED. The Orchestrator must NOT advance the team to a"
  echo " later phase until the missing items above are produced. Route"
  echo " the responsible upstream agents to finish them."
fi
echo "================================================================"
exit $overall_rc
