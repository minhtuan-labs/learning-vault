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

(none yet)

### 2026-05-16 17:25 — Tech Stack Confirmation Pending
Filed question SA_20260516_172526 asking user to confirm/override proposed stack: Next.js 15 + TypeScript + Tailwind + shadcn/ui (FE), NestJS + TypeScript (BE), PostgreSQL 16 + Prisma, sessions auth, pnpm, monorepo layout, Docker Compose for v1. Awaiting user answer in .pane_answers/ before proceeding to write TECH_STACK.md and SOLUTION_ARCHITECTURE.md.

### 2026-05-16 17:35 — Stack Confirmed & Architecture Docs Complete
User confirmed Python-based stack via .pane_answers/SA_20260516_172526.md: Dash (Plotly) + Tailwind (FE), FastAPI (BE), PostgreSQL 16 + SQLAlchemy + Alembic (data), JWT auth, local filesystem for images, monorepo (backend/ + frontend/), pip + poetry, Docker Compose for v1. Created: TECH_STACK.md (confirmed tech choices + rationale), SOLUTION_ARCHITECTURE.md (system design, components, data flow, security model), ADR.md (12 key decisions: monorepo, JWT stateless auth, single DB, single currency per family, local filesystem images, Docker Compose, soft deletes, REST API, SMTP email, same-DB audit logging, default categories), API_CONTRACT.md (detailed endpoint specs with examples). Ready for BE/FE/QA to begin planning phase 3.
