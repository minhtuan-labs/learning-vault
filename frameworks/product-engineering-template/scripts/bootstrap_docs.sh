#!/usr/bin/env bash
set -euo pipefail

# v10.5 — scaffold the docs/, planning/, reports/, code, and memory/
# skeletons for a new (or imported) project.

mkdir -p docs/product docs/architecture docs/business docs/qa docs/delivery \
         planning reports backend frontend memory

touch \
  docs/product/PRD.md \
  docs/product/ROADMAP.md \
  docs/product/UX_FLOW.md \
  docs/product/WIREFRAMES.md \
  docs/product/DESIGN_NOTES.md \
  docs/architecture/SOLUTION_ARCHITECTURE.md \
  docs/architecture/TECH_STACK.md \
  docs/architecture/ADR.md \
  docs/architecture/API_CONTRACT.md \
  docs/business/BUSINESS_REQUIREMENTS.md \
  docs/business/USER_STORIES.md \
  docs/business/DOMAIN_MODEL.md \
  docs/qa/TEST_PLAN.md \
  docs/qa/TEST_CASES.md \
  docs/delivery/DELIVERY_PLAN.md \
  docs/delivery/RELEASE_NOTES.md \
  docs/delivery/RUNNING_APP.md \
  planning/OPEN_QUESTIONS.md \
  planning/BACKLOG.md \
  planning/BE_PLAN.md \
  planning/FE_PLAN.md \
  reports/TEST_REPORT.md \
  reports/BUG_REPORT.md

# Seed memory/ skeleton if it doesn't exist yet (template ships these
# but a user who cherry-picked scripts/ may not have them).
ROLES=(ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY)
for role in "${ROLES[@]}"; do
  if [[ ! -f "memory/${role}.md" ]]; then
    cat > "memory/${role}.md" <<EOF
# Memory — ${role}

> Durable scratchpad for the **${role}** pane.
>
> READ this file at the start of every task (alongside
> \`memory/_PROJECT_STATE.md\`). APPEND a dated entry before exiting any
> OpenCode turn. See \`memory/README.md\` for format and discipline.

## Decisions

(none yet)

## Conventions

(none yet)

## Gotchas

(none yet)

## Open items I'm tracking

(none yet)
EOF
    echo "Created memory/${role}.md"
  fi
done

if [[ ! -f memory/_PROJECT_STATE.md ]]; then
  cat > memory/_PROJECT_STATE.md <<'EOF'
# Project State

> Owned by **ORCHESTRATOR**. Updated after every phase delegation
> and after each significant cross-phase event.

## Project name

(filled in once PRODUCT_IDEA.md exists)

## Current phase

NOT_STARTED

## Phase completion

- [ ] 0_DISCOVERY
- [ ] 1_SOLUTION_DESIGN
- [ ] 2_BACKLOG_AND_SPEC
- [ ] 3_IMPLEMENTATION_PLANNING
- [ ] 4_BUILD
- [ ] 5_TEST_AND_FIX
- [ ] 6_DELIVERY

## Active workstreams

(none yet)

## Known unresolved questions

(see scripts/list_pending_questions.sh for live list)

## Last live deploy

None yet.

## Session log

(append a one-liner each time the team starts/resumes work)
EOF
  echo "Created memory/_PROJECT_STATE.md"
fi

echo "Docs + memory scaffold ready."
