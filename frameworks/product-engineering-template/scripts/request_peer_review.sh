#!/usr/bin/env bash
set -euo pipefail

# v10.24 — Adversarial peer review of a design doc.
#
# WHY: code gets QA, but design docs (PRD, architecture, API contract)
# ship straight from their author with no second pair of eyes. This
# routes a structured review task to a DIFFERENT role's pane, which
# writes a verdicted review report. It's a thin, honest wrapper over
# route_to_pane.sh (real pane, real model) — no simulated review.
#
# Usage:
#   bash scripts/request_peer_review.sh <DOC> [REVIEWER_ROLE]
#
# If REVIEWER_ROLE is omitted, a sensible cross-role reviewer is picked:
#   PRD               -> SA   (can we build what PM scoped?)
#   SOLUTION_ARCH     -> BE   (is this architecture implementable?)
#   TECH_STACK        -> BE   (do the implementers accept the stack?)
#   API_CONTRACT      -> FE   (is the contract usable from the client?)
#   USER_STORIES      -> QA   (are these testable / have ACs?)
#   UX_FLOW           -> PM   (does the flow match product intent?)
#   (fallback)        -> SA
#
# The reviewer is told to write reports/REVIEW_<docbase>.md with a first
# line of `VERDICT: APPROVE` or `VERDICT: REVISE` plus specific findings,
# then notify the Orchestrator. The author role is never assigned to
# review its own doc.
#
# Exit codes: 0 routed, 1 author==reviewer or bad input, 2 usage error.

DOC="${1:-}"
REVIEWER="${2:-}"

if [[ -z "$DOC" ]]; then
  echo "Usage: bash scripts/request_peer_review.sh <DOC> [REVIEWER_ROLE]" >&2
  exit 2
fi

if [[ ! -f "$DOC" ]]; then
  echo "ERROR: doc not found: $DOC" >&2
  echo "       Review a doc that exists; produce it first if needed." >&2
  exit 1
fi

base="$(basename "$DOC")"

# Author (owner) of the doc — used to avoid self-review and to name it.
author_for() {
  case "$1" in
    docs/product/*)        echo "PM" ;;
    docs/business/*)       echo "BA" ;;
    docs/architecture/*)   echo "SA" ;;
    docs/qa/*|reports/*)   echo "QA" ;;
    *)                     echo "" ;;
  esac
}
AUTHOR="$(author_for "$DOC")"

if [[ -z "$REVIEWER" ]]; then
  case "$base" in
    PRD.md)                     REVIEWER="SA" ;;
    SOLUTION_ARCHITECTURE.md)   REVIEWER="BE" ;;
    TECH_STACK.md)              REVIEWER="BE" ;;
    API_CONTRACT.md)            REVIEWER="FE" ;;
    USER_STORIES.md)            REVIEWER="QA" ;;
    UX_FLOW.md)                 REVIEWER="PM" ;;
    *)                          REVIEWER="SA" ;;
  esac
fi

REVIEWER="$(echo "$REVIEWER" | tr '[:lower:]' '[:upper:]')"

VALID=" PM SA BA UX BE FE QA DELIVERY "
if [[ "$VALID" != *" $REVIEWER "* ]]; then
  echo "ERROR: invalid reviewer role: $REVIEWER" >&2
  echo "       Valid: PM SA BA UX BE FE QA DELIVERY" >&2
  exit 1
fi

if [[ -n "$AUTHOR" && "$REVIEWER" == "$AUTHOR" ]]; then
  echo "ERROR: $REVIEWER owns $DOC — a role cannot peer-review its own doc." >&2
  echo "       Pick a different reviewer role." >&2
  exit 1
fi

REVIEW_OUT="reports/REVIEW_${base}"

MSG="PEER REVIEW request. Read ${DOC} critically as ${REVIEWER}.
Do NOT rewrite it — review it. Write reports/REVIEW_${base} with:
 - First line EXACTLY: 'VERDICT: APPROVE' or 'VERDICT: REVISE'
 - Strengths (1-3 bullets)
 - Gaps / risks / ambiguities, each with the section it refers to
 - Concrete, actionable change requests if VERDICT is REVISE
Judge from your role's lens (implementability, testability, contract
usability, scope realism — whatever ${REVIEWER} cares about). Be
specific and terse. When done, notify the Orchestrator with the verdict
and the path ${REVIEW_OUT}."

echo "Routing peer review of ${DOC} to ${REVIEWER}${AUTHOR:+ (author=${AUTHOR})} -> ${REVIEW_OUT}"
exec bash scripts/route_to_pane.sh "$REVIEWER" "$MSG"
