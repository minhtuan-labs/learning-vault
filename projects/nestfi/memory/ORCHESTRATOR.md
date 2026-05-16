# Memory — ORCHESTRATOR

> Durable scratchpad for the **ORCHESTRATOR** pane. ORCHESTRATOR owns: routing work to the right pane and surfacing inbox events to the user.
>
> READ this file at the start of every task (alongside
> `memory/_PROJECT_STATE.md`). APPEND a dated entry before exiting any
> OpenCode turn. See `memory/README.md` for format and discipline.

## Decisions

(none yet)

## Conventions

(none yet)

## Gotchas

(none yet)

## Open items I'm tracking

(none yet)

### 2026-05-14 16:59 — advanced to 0_DISCOVERY
Phase gate 0_DISCOVERY passed; team can start 0_DISCOVERY work.

### 2026-05-16 17:22 — Product idea provided, routed PM & BA
User filled PRODUCT_IDEA.md with complete NestFi vision (family financial management, superadmin account, email invitations, multi-family). Answered pending questions for PM (now drafting PRD/ROADMAP) and BA (now drafting BUSINESS_REQUIREMENTS/DOMAIN_MODEL/USER_STORIES). UX watching for PRD auto-resume. Phase 0 DISCOVERY now unblocked.

### 2026-05-16 17:24 — advanced to 1_SOLUTION_DESIGN
Phase gate 0_DISCOVERY passed; team can start 1_SOLUTION_DESIGN work.

### 2026-05-16 17:24 — Phase 0 DISCOVERY complete, advanced to Phase 1_SOLUTION_DESIGN
PM delivered PRD, ROADMAP, BACKLOG (22 stories, 119pts, 5 epics), OPEN_QUESTIONS. BA delivered 37 user stories with acceptance criteria covering all workflows (superadmin, family mgmt, transactions, categories, dashboard). UX is working on UX_FLOW and DESIGN_NOTES (Phase 2 early start). Phase 0 gate passes. Advanced to Phase 1 and routed SA to design solution architecture with tech stack confirmation protocol (12 dims).

### 2026-05-16 17:33 — Tech stack confirmed, SA resumed
User chose Python-native stack: Dash (Plotly) + Tailwind for frontend (beautiful, dashboard-focused), FastAPI backend, PostgreSQL, SQLAlchemy+Alembic, JWT auth, local filesystem for images, professional monorepo structure. SA routed to finalize SOLUTION_ARCHITECTURE, TECH_STACK.md, ADR.md.

### 2026-05-16 17:38 — advanced to 3_IMPLEMENTATION_PLANNING
Phase gate 2_BACKLOG_AND_SPEC passed; team can start 3_IMPLEMENTATION_PLANNING work.

### 2026-05-16 17:38 — Phases 0-2 complete, Phase 3 underway
SA completed Phase 1 with 4 architecture docs (TECH_STACK, SOLUTION_ARCHITECTURE, 12 ADRs, API_CONTRACT). Phase 2 was already complete (BACKLOG/USER_STORIES done in Phase 0). Advanced to Phase 3_IMPLEMENTATION_PLANNING. BE completed BE_PLAN (21 P0 endpoints, 6-7 day timeline); FE completed FE_PLAN (6-page Dash architecture, APIClient abstraction). Routed QA and DELIVERY to complete TEST_PLAN and DELIVERY_PLAN. Ready for Phase 4 BUILD once planning complete.

### 2026-05-16 17:46 — advanced to 4_BUILD
Phase gate did NOT pass but ADVANCE_PHASE_FORCE was used. User accepted the risk.

### 2026-05-16 17:46 — Phase 4 BUILD started, BE + FE routed
QA completed TEST_PLAN.md (110 unit tests, 78 integration tests, 49+ manual cases, Phase 5 exit gate defined). DELIVERY blocked by circular dependency (needs Phase 5 TEST_REPORT output). Forced Phase 3→4 advancement (ADVANCE_PHASE_FORCE=1) per user request. Routed BE and FE to code simultaneously: BE targeting 21 P0 endpoints in 6-7 days (FastAPI modules: auth, users, families, transactions, categories, admin); FE targeting 6 pages (login, family selector, dashboard, ledger, settings, invitations) in Dash + Tailwind. Both will commit incrementally and notify on milestones.

### 2026-05-16 17:49 — Phase 4 BUILD scaffolds complete for both BE and FE
BE completed backend scaffold (36 Python files): 7 API route modules (auth, users, families, transactions, categories, analytics, admin), 6 models, 9 schemas, CRUD ops, JWT+bcrypt auth, RBAC, soft deletes, tests. FE completed frontend scaffold (17 Python files): 6 Dash pages (login, family_selector, dashboard, ledger, settings, invitations), 5 component modules, centralized APIClient with 18 methods, Plotly charts, 10s polling. Both ready for callback wiring and integration testing. Moving toward Phase 5 (TEST_AND_FIX) and Phase 6 (DELIVERY).
