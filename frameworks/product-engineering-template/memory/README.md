# `memory/` — durable cross-session memory for the agent team

This directory is the team's **shared, persistent notebook**. It is
intentionally **committed to git** — unlike `.pane_logs/`,
`.pane_tasks/`, etc. which are per-session runtime artefacts.

## Why this exists

Workers in this framework run one-shot (`opencode run --model X
"<task>"`) and exit. Without an explicit memory layer, every task
would start from scratch and forget everything decided in previous
sessions. That's expensive (re-deriving the same answers) and risky
(decisions drift, conventions are silently re-invented).

`memory/<ROLE>.md` is each agent's append-only scratchpad of
**decisions, conventions, and gotchas** that don't already live in
a canonical doc. `memory/_PROJECT_STATE.md` is the team's shared
"where are we" snapshot, owned by the Orchestrator.

When you re-run `bash scripts/start_agents_tmux.sh <project>` the
next day, the framework detects this directory, runs in "resume
mode", and tells each agent to re-read its memory before doing any
work. The team comes back to the same state, not a fresh project.

## What goes here (and what does NOT)

Put in `memory/<ROLE>.md`:

- "I chose Postgres because user said 'free Supabase tier'"
- "Convention: all timestamps stored UTC, displayed Asia/Ho_Chi_Minh"
- "Gotcha: macOS Docker can't bind port 3000 — using 3001 for FE"
- "FYI BE keeps DB connections in a pool of size 20"
- "If you change the auth header, also update `FE_PLAN §4`"

Do NOT put here (these have canonical homes):

- Architecture decisions → `docs/architecture/ADR.md`
- Business rules / acceptance criteria → `docs/business/USER_STORIES.md`
- Test cases → `docs/qa/TEST_CASES.md`
- Implementation plans → `planning/BE_PLAN.md`, `planning/FE_PLAN.md`
- The PRD → `docs/product/PRD.md`

`memory/` is for the connective tissue between those documents —
the "why did we …" / "remember that …" notes that help future-you
(or a different model) pick up where this-you left off.

## File format

Append-only Markdown. Each entry starts with a level-3 heading
containing the date+time and a short title:

```markdown
### 2026-05-14 18:30 — Postgres on Supabase free tier
Chose Postgres over MongoDB because the user specifically wants the
free Supabase tier (.pane_answers/SA_20260514_080000.md). All schemas
use UUIDv7 primary keys; ULIDs were considered but Supabase has no
native helper for them yet.
```

Sections inside each role file (optional but useful):

- `## Decisions`         — choices that affect future work
- `## Conventions`       — naming, formatting, structural rules
- `## Gotchas`           — things that bit us; future-you will thank
                           past-you
- `## Open items I'm tracking` — short-term todos that don't belong
                           in BACKLOG yet

Keep entries short (2-5 lines). The point is recall, not depth — link
out to the real doc if you need more.

## The discipline

Every worker is prompted to:

- READ `memory/_PROJECT_STATE.md` and `memory/<ROLE>.md` at the start
  of every task, BEFORE doing any work.
- APPEND a fresh entry to `memory/<ROLE>.md` before exiting the
  current OpenCode turn (or write "no new entries" if nothing
  changed).

The Orchestrator is additionally prompted to update
`memory/_PROJECT_STATE.md` after every phase delegation so the
"current phase / active workstreams / unresolved questions" stay
fresh.

If memory drifts (worker forgot to update, or `_PROJECT_STATE.md`
points at an old phase), the user can run
`bash scripts/rescan_project.sh` to see actual file system state and
correct the memory manually.
