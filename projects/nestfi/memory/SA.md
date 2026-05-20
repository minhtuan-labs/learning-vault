# Memory — SA

> Durable scratchpad for the **SA** pane. SA owns: solution architecture, tech stack, API contract.
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

- 2026-05-16 21:44:16 — Awaiting tech stack confirmation (SA_20260516_214416). Proposed: Next.js+TS, FastAPI+Python, PostgreSQL+SQLAlchemy, session auth, Docker Compose, monorepo. Waiting for user answer to proceed with TECH_STACK.md, ADR.md, SOLUTION_ARCHITECTURE.md, API_CONTRACT.md.

### 2026-05-16 21:56 — Phase 1 SOLUTION_DESIGN complete
User confirmed tech stack with JWT + Session auth dual support. Wrote four architecture documents:
- TECH_STACK.md: Full tech stack table with rationales (Next.js, FastAPI, PostgreSQL, SQLAlchemy, session + JWT auth, Docker Compose, monorepo)
- SOLUTION_ARCHITECTURE.md: System topology, boundary definitions, DB schema outline, API layer routing
- ADR.md: 10 architecture decisions (synchronous monolith, family-scoped isolation, session+JWT, account-centric, edit audit trail, soft/hard-delete, monorepo, mock email, Docker Compose v1, SQLAlchemy+Alembic)
- API_CONTRACT.md: Full REST endpoint specs, request/response examples, error handling, auth flows
Ready for BE/FE review and implementation planning.
