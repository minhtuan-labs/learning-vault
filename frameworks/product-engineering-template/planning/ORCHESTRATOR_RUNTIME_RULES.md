# Orchestrator Runtime Rules — v10

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

Each pane role has its own OpenCode model. Internal subagents would keep
all work inside the Orchestrator's session and on the Orchestrator's
model, defeating the multi-model design.
