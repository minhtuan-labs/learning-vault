#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-}"

if [[ -z "$PHASE" ]]; then
  echo "Usage: bash scripts/delegate_phase.sh <phase>"
  echo "Available phases: discovery, solution, backlog, planning, build, test, delivery, release"
  exit 1
fi

# v10.9 — warn if the phase before this one isn't done. Doesn't refuse
# (the user might be intentionally retrying / patching), but the
# Orchestrator should surface the warning to the user and decide.
warn_if_prev_phase_incomplete() {
  local target_full_phase="$1"
  local prev_phase=""
  case "$target_full_phase" in
    1_SOLUTION_DESIGN)         prev_phase="0_DISCOVERY" ;;
    2_BACKLOG_AND_SPEC)        prev_phase="1_SOLUTION_DESIGN" ;;
    3_IMPLEMENTATION_PLANNING) prev_phase="2_BACKLOG_AND_SPEC" ;;
    4_BUILD)                   prev_phase="3_IMPLEMENTATION_PLANNING" ;;
    5_TEST_AND_FIX)            prev_phase="4_BUILD" ;;
    6_DELIVERY)                prev_phase="5_TEST_AND_FIX" ;;
    *) return 0 ;;
  esac
  if [[ -x scripts/check_phase_gate.sh ]]; then
    if ! bash scripts/check_phase_gate.sh "$prev_phase" >/dev/null 2>&1; then
      echo "============================================================"
      echo "  WARNING: previous phase ($prev_phase) is INCOMPLETE."
      echo "  Run 'bash scripts/check_phase_gate.sh $prev_phase' to see"
      echo "  what's missing. Continuing this delegation anyway — the"
      echo "  Orchestrator should decide whether to route the upstream"
      echo "  agents first instead of barrelling forward."
      echo "============================================================"
    fi
  fi
}

route() {
  local role="$1"
  local message="$2"
  bash scripts/route_to_pane.sh "$role" "$message"
}

case "$PHASE" in
  discovery|0|0_DISCOVERY)
    route PM "You are PM. Task: convert PRODUCT_IDEA.md into product scope. Read PRODUCT_IDEA.md, PRODUCT_ENGINEERING.md, TASK.md, planning/PANE_ROUTING_RULES.md. Write/update docs/product/PRD.md, docs/product/ROADMAP.md, planning/OPEN_QUESTIONS.md. Do not write code. When done, summarize changed files and route a concise completion note to ORCHESTRATOR if needed."
    route BA "You are BA. Task: clarify business requirements. Read PRODUCT_IDEA.md, PRODUCT_ENGINEERING.md, TASK.md, planning/PANE_ROUTING_RULES.md. Write/update docs/business/BUSINESS_REQUIREMENTS.md, docs/business/DOMAIN_MODEL.md, docs/business/USER_STORIES.md. Do not write code. When done, summarize changed files and route a concise completion note to ORCHESTRATOR if needed."
    route UX "You are UX. Task: draft initial user journey and screen flow. Read PRODUCT_IDEA.md, docs/product/PRD.md if available, TASK.md, planning/PANE_ROUTING_RULES.md. Write/update docs/product/UX_FLOW.md, docs/product/WIREFRAMES.md, docs/product/DESIGN_NOTES.md. Do not implement UI code. When done, summarize changed files and route a concise completion note to ORCHESTRATOR if needed."
    ;;
  solution|1|1_SOLUTION_DESIGN)
    warn_if_prev_phase_incomplete 1_SOLUTION_DESIGN
    route SA "You are SA. Task: design solution architecture for this project. MANDATORY FIRST STEP: follow the Tech Stack Confirmation Protocol in prompts/agents/SA.md — read PRODUCT_IDEA.md and docs/product/PRD.md, then call bash scripts/ask_orchestrator.sh SA with a batched proposal covering frontend framework, frontend language, UI/design system, backend language, backend framework, primary datastore, ORM, auth approach, cache/queue, hosting target, code layout, and package manager. Exit and wait for the user's answer. DO NOT write docs/architecture/TECH_STACK.md or docs/architecture/ADR.md or docs/architecture/SOLUTION_ARCHITECTURE.md before that answer arrives. After answer_role.sh resumes you with .pane_answers/SA_<qid>.md, write all four files quoting the user's choices verbatim and including 'Confirmed by user (question id: SA_<qid>)' at the top of TECH_STACK.md. Then update memory/SA.md. Finally summarize changed files."
    ;;
  backlog|2|2_BACKLOG_AND_SPEC)
    warn_if_prev_phase_incomplete 2_BACKLOG_AND_SPEC
    route PM "You are PM. Task: refine MVP scope and priorities. Read docs/product/PRD.md, docs/business/USER_STORIES.md, docs/product/UX_FLOW.md, docs/architecture/SOLUTION_ARCHITECTURE.md. Update planning/BACKLOG.md and docs/product/ROADMAP.md. Summarize changed files."
    route BA "You are BA. Task: refine user stories and acceptance criteria. Read docs/product/PRD.md, docs/business/BUSINESS_REQUIREMENTS.md, docs/product/UX_FLOW.md. Update docs/business/USER_STORIES.md and planning/BACKLOG.md. Summarize changed files."
    route UX "You are UX. Task: refine UX flow based on business requirements. Read docs/business/USER_STORIES.md and docs/architecture/API_CONTRACT.md. Update docs/product/UX_FLOW.md, docs/product/WIREFRAMES.md, docs/product/DESIGN_NOTES.md. Summarize changed files."
    route SA "You are SA. Task: refine API contract and technical boundaries based on backlog. Read planning/BACKLOG.md, docs/business/USER_STORIES.md, docs/product/UX_FLOW.md. Update docs/architecture/API_CONTRACT.md and docs/architecture/ADR.md. Summarize changed files."
    ;;
  planning|3|3_IMPLEMENTATION_PLANNING)
    warn_if_prev_phase_incomplete 3_IMPLEMENTATION_PLANNING
    route BE "You are BE. Task: backend implementation planning only. Read docs/architecture/SOLUTION_ARCHITECTURE.md, docs/architecture/API_CONTRACT.md, planning/BACKLOG.md, docs/business/USER_STORIES.md. Write/update planning/BE_PLAN.md. Do not code until TASK.md phase is 4_BUILD or Orchestrator confirms. Summarize changed files."
    route FE "You are FE. Task: frontend implementation planning only. Read docs/product/UX_FLOW.md, docs/product/WIREFRAMES.md, docs/architecture/API_CONTRACT.md, planning/BACKLOG.md. Write/update planning/FE_PLAN.md. Do not code until TASK.md phase is 4_BUILD or Orchestrator confirms. Summarize changed files."
    route QA "You are QA. Task: test planning. Read planning/BACKLOG.md, docs/business/USER_STORIES.md, docs/architecture/API_CONTRACT.md, docs/product/UX_FLOW.md. Write/update docs/qa/TEST_PLAN.md and docs/qa/TEST_CASES.md. Summarize changed files."
    route DELIVERY "You are DELIVERY. Task: delivery planning. Read docs/architecture/TECH_STACK.md, planning/BE_PLAN.md, planning/FE_PLAN.md if available. Write/update docs/delivery/DELIVERY_PLAN.md. Do not commit/push. Summarize changed files."
    ;;
  build|4|4_BUILD)
    warn_if_prev_phase_incomplete 4_BUILD
    route BE "You are BE. Task: implement backend according to planning/BE_PLAN.md. Read docs/architecture/API_CONTRACT.md, docs/business/USER_STORIES.md, planning/BACKLOG.md, TASK.md. Write backend code and backend tests only. When done, summarize changed files and route QA a test request."
    route FE "You are FE. Task: implement frontend according to planning/FE_PLAN.md. Read docs/product/UX_FLOW.md, docs/architecture/API_CONTRACT.md, planning/BACKLOG.md, TASK.md. Write frontend code and frontend tests only. When done, summarize changed files and route QA a test request."
    ;;
  test|5|5_TEST_AND_FIX)
    warn_if_prev_phase_incomplete 5_TEST_AND_FIX
    route QA "You are QA. Task: execute the test suites for this release. Steps: (1) Read docs/qa/TEST_PLAN.md, docs/qa/TEST_CASES.md, planning/BACKLOG.md, docs/business/USER_STORIES.md. (2) If critical user stories have no test yet, write the missing tests OR route BE/FE to write them — do not skip them. (3) Actually run the tests with the right runner for the stack (pytest, jest/vitest, etc.) and capture stdout+stderr. (4) Write reports/TEST_REPORT.md whose FIRST non-blank line is exactly 'VERDICT: PASS' or 'VERDICT: FAIL' — DELIVERY parses this. Then add date, build target, counts, per-suite summary, failures, gaps. (5) On FAIL: file bugs in reports/BUG_REPORT.md and run bash scripts/route_to_pane.sh BE/FE for fixes + bash scripts/notify_orchestrator.sh QA \"Tests FAIL — release blocked\". DO NOT route DELIVERY. (6) On PASS: run bash scripts/notify_orchestrator.sh QA \"Tests PASS — routing DELIVERY to deploy\" AND bash scripts/route_to_pane.sh DELIVERY \"Tests passed. Read reports/TEST_REPORT.md (VERDICT: PASS). Confirm ports with user via ask_orchestrator.sh if not done yet, then build images, run docker compose up --build -d, verify endpoints, write docs/delivery/RUNNING_APP.md, and notify Orchestrator with the URL.\""
    ;;
  delivery|6|6_DELIVERY)
    warn_if_prev_phase_incomplete 6_DELIVERY
    route DELIVERY "You are DELIVERY. Task: deploy the release. Steps: (1) Read reports/TEST_REPORT.md FIRST. If the first non-blank line is not 'VERDICT: PASS' — STOP. Run bash scripts/notify_orchestrator.sh DELIVERY 'Release blocked — TEST_REPORT.md is not PASS' and exit. (2) Inventory the stack from docs/architecture/TECH_STACK.md, planning/BE_PLAN.md, planning/FE_PLAN.md. (3) If docker-compose.yml does not exist, FIRST call bash scripts/ask_orchestrator.sh DELIVERY 'Suggested host ports: FE=3000, BE=8000, DB=5432. OK with these defaults, or specify different ones?' and pause until answered. (4) Author backend/Dockerfile, frontend/Dockerfile, docker-compose.yml, .env.example using the confirmed ports. Multi-stage builds, pinned base images, healthchecks, depends_on with service_healthy. (5) Run: docker compose build 2>&1 | tee docs/delivery/_last_build.log . On failure, route BE or FE with the log and exit. (6) Run: docker compose up --build -d. Then docker compose ps. Probe with curl http://localhost:<FE_PORT>/ and curl http://localhost:<BE_PORT>/health. (7) Write docs/delivery/RUNNING_APP.md with date, FE URL, BE URL, healthcheck URL, docker compose ps output, stop/log commands. (8) Append a dated entry to docs/delivery/RELEASE_NOTES.md. (9) Notify the Orchestrator with the live URL: bash scripts/notify_orchestrator.sh DELIVERY 'App is live — frontend at http://localhost:<FE_PORT> — see docs/delivery/RUNNING_APP.md'. Do not git push unless the user explicitly asks."
    ;;
  release|7|7_RELEASE)
    # Convenience: run test phase. QA will auto-route DELIVERY on PASS.
    bash "$0" test
    echo "Routed: test (DELIVERY will be auto-routed by QA if tests PASS)."
    exit 0
    ;;
  *)
    echo "Unknown phase: $PHASE"
    echo "Available phases: discovery, solution, backlog, planning, build, test, delivery, release"
    exit 1
    ;;
esac

echo "Routed phase: $PHASE"
