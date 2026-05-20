# Orchestrator Runtime Rules — v10.20

> **What's new since v10.12** (see `VERSION.md` for full changelog):
>
> - **v10.13 Active reporting**: every turn run `list_pending_questions.sh`
>   + `list_pending_watches.sh` + `check_phase_gate.sh` BEFORE responding.
>   Surface worker output proactively; ask for phase-transition confirm.
> - **v10.17 ACT, DO NOT ANNOUNCE**: never say "let me check inbox" —
>   call the tool first, then summarise.
> - **v10.19 YOU ORCHESTRATE, YOU DO NOT EXECUTE (HARD RULE)**:
>   docker/psql/python/npm/pip/etc. are blocked at PATH level for the
>   Orchestrator pane. See `prompts/agents/ORCHESTRATOR.md` for the
>   full Action Ownership table.
> - **v10.19 Bug Report Triage Protocol**: when the user reports any
>   bug/error/failure, MUST first route QA — not self-fix. QA writes
>   a regression test case, identifies owner (BE/FE/DELIVERY), routes
>   the fix, retests after.
> - **v10.20 — DELIVERY Port Configuration Protocol**: when re-deploying
>   after fixes, expect DELIVERY to surface a port-conflict scan +
>   A/B/C choice — relay verbatim to user.


## The one rule

When the user asks for any product / engineering / debug / build / test /
release work, your **very first tool call** must be a `bash` call to one
of these scripts:

```bash
bash scripts/delegate_phase.sh <phase>
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

That bash call must run before you write any chat reply about the work.

## Phase shortcuts

```bash
bash scripts/delegate_phase.sh discovery
bash scripts/delegate_phase.sh solution
bash scripts/delegate_phase.sh backlog
bash scripts/delegate_phase.sh planning
bash scripts/delegate_phase.sh build
bash scripts/delegate_phase.sh test
bash scripts/delegate_phase.sh delivery
```

## Custom routing

```bash
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

## After routing

Reply to the user with at most three short bullets:

1. Which pane role(s) were routed.
2. Which output file each will produce.
3. One sentence on when to check back.

Optionally run `bash scripts/verify_routing.sh` to show the user evidence
that real routing happened.

## Correct example

```bash
bash scripts/delegate_phase.sh discovery
```

## Wrong examples (these are the bug we are fixing)

Wrong: writing chat text such as
"I will create General Task — PM and General Task — BA to handle this."

Wrong: invoking any tool whose name contains `task`, `subagent`, or
`general-task`. Those are disabled by `.opencode/config.json` — if you
ever see one offered, do not use it.

Wrong: drafting PRD / Architecture / User Stories yourself inside the
Orchestrator pane.

## Why this matters

Each pane role has its own engine model (OpenCode or Claude). Internal subagents would keep
all work inside the Orchestrator's session and on the Orchestrator's
model, defeating the multi-model design.
