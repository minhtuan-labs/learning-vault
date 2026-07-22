#!/usr/bin/env bash
set -euo pipefail

# v10.24 — Content-quality gate for deliverable docs.
#
# check_phase_gate.sh proves a file EXISTS and is bigger than a byte
# threshold. That catches "file missing" but not "file is 600 bytes of
# headings with no acceptance criteria". This script checks that key
# docs actually contain their REQUIRED SECTIONS / MARKERS — a shallow
# structural schema, not a deep review (that's what request_peer_review.sh
# is for).
#
# Each doc maps to a list of "label::regex" requirements. A doc passes
# only if every requirement's regex matches somewhere in the file
# (case-insensitive). Missing files are reported but do NOT fail this
# script by default — absence is check_phase_gate.sh's job; this script
# judges the QUALITY of files that are present. Pass --require-present
# to also fail on missing files.
#
# Usage:
#   bash scripts/check_doc_schema.sh                 # check every known doc that exists
#   bash scripts/check_doc_schema.sh <phase>         # only docs for one phase
#   bash scripts/check_doc_schema.sh --file <path>   # one specific doc
#   bash scripts/check_doc_schema.sh --require-present <phase>
#
# Phases: 0_DISCOVERY 1_SOLUTION_DESIGN 2_BACKLOG_AND_SPEC
#         3_IMPLEMENTATION_PLANNING 5_TEST_AND_FIX
#
# Exit codes: 0 all present docs satisfy their schema, 1 a present doc
# is incomplete (or a required doc missing under --require-present),
# 2 usage error.

REQUIRE_PRESENT=false
if [[ "${1:-}" == "--require-present" ]]; then
  REQUIRE_PRESENT=true; shift
fi

SINGLE_FILE=""
if [[ "${1:-}" == "--file" ]]; then
  SINGLE_FILE="${2:-}"; shift 2 || true
fi

PHASE="${1:-ALL}"

# Schema table. Format per requirement: "label::regex"
# Requirements are intentionally lenient on wording (alternations) so
# they reward substance without dictating a single template.
# Each case prints one requirement per line as "label::regex". Labels may
# contain spaces; parsing is line-based (no eval/word-splitting).
schema_for() {
  case "$1" in
    docs/product/PRD.md)
      printf '%s\n' \
        "Problem statement::problem|pain" \
        "Target users / personas::target user|persona|audience" \
        "Goals / objectives::goal|objective" \
        "Scope or MVP::scope|mvp|must-have|in scope" \
        "Success metrics::success metric|kpi|metric" ;;
    docs/business/USER_STORIES.md)
      printf '%s\n' \
        "User-story form::as a .* i want|as an .* i want|user story" \
        "Acceptance criteria::acceptance criteria|given .* when .* then|given/when/then" ;;
    docs/business/BUSINESS_REQUIREMENTS.md)
      printf '%s\n' \
        "Business rules::business rule|rule|constraint" \
        "Requirements list::requirement|shall|must" ;;
    docs/product/UX_FLOW.md)
      printf '%s\n' \
        "Flow / steps::flow|step|screen|journey" \
        "Entry or happy path::happy path|entry|start|primary flow" ;;
    docs/architecture/SOLUTION_ARCHITECTURE.md)
      printf '%s\n' \
        "Components::component|service|module" \
        "Data flow / interaction::data flow|sequence|interaction|request|response" ;;
    docs/architecture/TECH_STACK.md)
      printf '%s\n' \
        "Stack choices::frontend|backend|database|datastore|language|framework" \
        "User confirmation (v10.7)::confirmed by user" ;;
    docs/architecture/API_CONTRACT.md)
      printf '%s\n' \
        "Endpoints::endpoint|GET |POST |PUT |DELETE |/api|path" \
        "Schemas / payloads::request|response|payload|schema|body" ;;
    docs/architecture/ADR.md)
      printf '%s\n' \
        "Decision record::decision|status|context|consequence" ;;
    docs/qa/TEST_PLAN.md)
      printf '%s\n' \
        "Test scope::scope|in scope|coverage" \
        "Test scenarios / cases::scenario|test case|case id|tc[0-9]" ;;
    reports/TEST_REPORT.md)
      printf '%s\n' \
        "Verdict line::verdict:[[:space:]]*(pass|fail)" \
        "Evidence::test|result|stdout|passed|failed" ;;
    *) echo "" ;;
  esac
}

phase_docs() {
  case "$1" in
    0_DISCOVERY)
      echo "docs/product/PRD.md docs/business/BUSINESS_REQUIREMENTS.md docs/business/USER_STORIES.md docs/product/UX_FLOW.md" ;;
    1_SOLUTION_DESIGN)
      echo "docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/architecture/ADR.md docs/architecture/API_CONTRACT.md" ;;
    2_BACKLOG_AND_SPEC)
      echo "docs/business/USER_STORIES.md docs/architecture/API_CONTRACT.md" ;;
    3_IMPLEMENTATION_PLANNING)
      echo "docs/qa/TEST_PLAN.md" ;;
    5_TEST_AND_FIX)
      echo "reports/TEST_REPORT.md" ;;
    ALL)
      echo "docs/product/PRD.md docs/business/BUSINESS_REQUIREMENTS.md docs/business/USER_STORIES.md docs/product/UX_FLOW.md docs/architecture/SOLUTION_ARCHITECTURE.md docs/architecture/TECH_STACK.md docs/architecture/ADR.md docs/architecture/API_CONTRACT.md docs/qa/TEST_PLAN.md reports/TEST_REPORT.md" ;;
    *) echo "" ;;
  esac
}

# Returns 0 if doc passes (or is absent & not required), 1 otherwise.
check_doc() {
  local doc="$1" reqs label regex fails=0 present=0
  reqs="$(schema_for "$doc")"
  if [[ -z "$reqs" ]]; then
    echo "  $doc — (no schema defined, skipped)"
    return 0
  fi
  if [[ ! -f "$doc" ]]; then
    if $REQUIRE_PRESENT; then
      echo "  $doc — MISSING (required)"
      return 1
    fi
    echo "  $doc — absent (skipped; existence is check_phase_gate.sh's job)"
    return 0
  fi
  echo "  $doc:"
  while IFS= read -r req; do
    [[ -z "$req" ]] && continue
    label="${req%%::*}"
    regex="${req#*::}"
    if grep -qiE "$regex" "$doc" 2>/dev/null; then
      printf "    [ok]   %s\n" "$label"
    else
      printf "    [MISS] %s  (looked for /%s/)\n" "$label" "$regex"
      fails=$(( fails + 1 ))
    fi
  done <<< "$reqs"
  if (( fails > 0 )); then
    echo "    -> INCOMPLETE (${fails} requirement(s) unmet)"
    return 1
  fi
  echo "    -> OK"
  return 0
}

echo "================================================================"
echo " Document schema check  (content quality, not just existence)"
echo "================================================================"

rc=0

if [[ -n "$SINGLE_FILE" ]]; then
  check_doc "$SINGLE_FILE" || rc=1
else
  docs="$(phase_docs "$PHASE")"
  if [[ -z "$docs" ]]; then
    echo "Unknown phase: $PHASE" >&2
    exit 2
  fi
  for d in $docs; do
    check_doc "$d" || rc=1
  done
fi

echo "----------------------------------------------------------------"
if (( rc == 0 )); then
  echo " All checked docs satisfy their content schema."
else
  echo " One or more docs are INCOMPLETE. Route the owning role to fill"
  echo " the missing sections, or run a peer review:"
  echo "   bash scripts/request_peer_review.sh <doc> <REVIEWER_ROLE>"
fi
echo "================================================================"
exit $rc
