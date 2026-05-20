# Memory — PM

> Durable scratchpad for the **PM** pane. PM owns: product scope, PRD, roadmap, MVP boundary.
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

### 2026-05-16 21:25 — Phase 0 Discovery: PRD, Roadmap, Open Questions
**Summary**: Converted PRODUCT_IDEA.md into product scope documents. Created detailed PRD (9 sections + acceptance criteria), 3-phase roadmap (v1.0 MVP → v1.1 Polish → v1.2 UX), and identified 10 open questions (3 blocking user decisions). MVP scope locked to core features (auth, family mgmt, transaction CRUD, dashboard, analytics). Bill splitting, recurring transactions, and mobile app deferred to post-MVP phases. Key conventions: MoSCoW prioritization, role-based access control architecture, household-focused (not business accounting). Next: route open questions to user for decisions before proceeding to Phase 1 (Solution Design).

### 2026-05-16 21:37 — User clarification: Account-centric model, bill-splitting deferred
**Summary**: User clarified Q1 vision: NestFi is account-centric (tracks which account money comes from, not person-to-person bill-splitting). Cash withdrawal = single transaction, not detailed sub-tracking. Updated PRD to emphasize account-based model and clarify scope. Resolved Q1 (bill-splitting → v2.0) and Q6 (cash withdrawal → one-time entry only) in OPEN_QUESTIONS.md. 5 questions remain blocking/high-priority. MVP scope remains lean and focused on household account tracking.

### 2026-05-16 21:42 — User clarification: All blocking questions resolved, MVP finalized
**Summary**: User answered remaining clarification questions: Q2 (force password change on first login for all users), Q3 (family selector at login + in-dashboard switcher), Q6 (session timeout = NEVER, manual logout only), Q8 (include export reports in v1.0). Updated PRD and ROADMAP to reflect these decisions. Added password change flow, family selector UI, export reports feature, and session management model to v1.0 MVP deliverables. Expanded acceptance criteria from 9 to 16 items. OPEN_QUESTIONS.md updated with all user decisions. **Phase 0_DISCOVERY COMPLETE** — all blocking decisions resolved. Ready to advance to Phase 1_SOLUTION_DESIGN.

### 2026-05-16 21:59 — Phase 2 BACKLOG_AND_SPEC: MVP scope refined, backlog and roadmap finalized
**Summary**: Converted PRD and user stories into prioritized backlog using MoSCoW framework. 14 MUST stories (v1.0 MVP) grouped into 4 milestones: Auth & Family Foundation (week 1), Finance & Transactions (week 2), Dashboard & Reports (week 3), Polish & Security (v1.1+). BACKLOG.md now includes detailed story tables, acceptance criteria, dependencies, and implementation sequencing. ROADMAP.md updated with specific deliverables per phase, resource allocation, and gate criteria. Key conventions established: account-centric model (not person-to-person bill-splitting), full family transparency, edit audit trail for compliance, soft-delete + hard-delete pattern. Identified blockers for Phase 4_BUILD: Email service provider must be configured before development starts. Ready to advance to Phase 3_IMPLEMENTATION_PLANNING.
