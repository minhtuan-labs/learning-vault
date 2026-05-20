# Agent Workflow and Delegation Protocol — v10.23

> **What's new since v10.12** (see `VERSION.md` for full changelog):
>
> - **v10.21 PaneC team** — team of 9 = PaneC. Orches (display) /
>   ORCHESTRATOR (internal). Deli (display) / DELIVERY (internal).
>   PM/SA/BA/UX/BE/FE/QA keep two-letter codes for both.
> - **v10.22 Deli port protocol** — exhaustive port scan (host +
>   running docker + stopped docker + nearby compose files) before
>   every compose-up, post-up `--verify` probe before
>   `RUNNING_APP.md` write.
> - **v10.23 Layer-4 hook** — `PreToolUse` hook on Write/Edit blocks
>   Orchestrator from editing owner-specific files via Claude's
>   native tools (PATH guard alone doesn't cover this). Workers
>   unaffected.
>
> - **v10.13 Complete-and-notify mandate**: every worker MUST call
>   `notify_orchestrator.sh <ROLE> "Done — <paths>. Summary: …"` as
>   the last action before exit, even when the worker thinks it's
>   "obviously done". v10.18 added a framework safety net that
>   auto-fires this notify if the worker forgot.
> - **v10.14 Auto-resume on dependency unlock**: workers blocked on
>   a missing upstream file call `scripts/file_watch.sh <ROLE> <FILE> "<task>"`
>   and exit. The background `scripts/watcher_daemon.sh` auto-reroutes
>   them when `<FILE>` lands.
> - **v10.16 `--free` overlay**: `start_agents_tmux.sh --free` sources
>   `config/engines/<engine>-free.env` to force every role to a
>   free-tier model. Useful for workflow iteration without burning
>   paid credits.
> - **v10.18 Heartbeat for long-running tasks**: worker shell wrapper
>   `touch`es `.pane_heartbeats/<ROLE>.beat` every 10s; the watcher
>   daemon flags stalls > 90s old.
> - **v10.19/20 Stay-in-lane hardening**: Orchestrator PATH guard
>   blocks engineering commands; DELIVERY has a hard Port
>   Configuration Protocol.


## Runtime

Only Orchestrator runs the interactive engine TUI. The other 8 panes stay as
idle shells until `route_to_pane.sh` (or `delegate_phase.sh`) starts
the engine in them with that pane's configured model. Every delegated
task therefore runs under the target role's model, not Orchestrator's.

## Strict delegation rule

The engine's built-in `Task` / `general-task` subagent tool is
disabled by the engine's config file (`.opencode/config.json` or
`.claude/settings.json`) (see `config/OPENCODE_PERMISSION_POLICY.md`).
Every cross-role handoff must be a real shell command:

```bash
bash scripts/route_to_pane.sh <AGENT> "<message>"
```

or, for phase-level delegation (Orchestrator only):

```bash
bash scripts/delegate_phase.sh <phase>
```

If you only describe delegation in chat, the target pane will not run.
Use `bash scripts/verify_routing.sh` to confirm a real handoff fired.

Worker panes execute delegated tasks with:

```bash
# Engine=opencode:
OPENCODE_CONFIG=<project>/.opencode/config.json \
  opencode run --model <target_agent_model> "<task prompt>"

# Engine=claude:
claude --print --model <target_agent_model> "<task prompt>"
```

## Core rule

Each major task must run in the pane of the agent that owns that task.

Do not simulate another agent inside your own pane.

If another agent needs to act, send that agent an explicit message using:

```bash
bash scripts/route_to_pane.sh <AGENT> "<message>"
```

## Delegation rule

When you delegate:
1. Run the shell command.
2. Do not merely describe the task.
3. Tell the target agent which files to read.
4. Tell the target agent which files to create/update.
5. Tell the target agent when to report back.

## Standard message format

```text
You are <AGENT>. Task: <specific task>.
Read: <files>.
Write/update: <files>.
Constraints: <important rules>.
When done: summarize output and notify <NEXT_AGENT or ORCHESTRATOR>.
```

## Phase ownership

| Phase | Primary agents | Next handoff |
|---|---|---|
| 0_DISCOVERY | PM, BA, UX | ORCHESTRATOR |
| 1_SOLUTION_DESIGN | SA | ORCHESTRATOR, then BE/FE/QA |
| 2_BACKLOG_AND_SPEC | PM, BA, UX, SA | ORCHESTRATOR |
| 3_IMPLEMENTATION_PLANNING | BE, FE, QA, DELIVERY | ORCHESTRATOR |
| 4_BUILD | BE, FE | QA |
| 5_TEST_AND_FIX | QA, BE, FE | DELIVERY |
| 6_DELIVERY | DELIVERY | ORCHESTRATOR |

## Handoff examples

SA to BE/FE:

```bash
bash scripts/route_to_pane.sh BE "You are BE. Read docs/architecture/SOLUTION_ARCHITECTURE.md and docs/architecture/API_CONTRACT.md. Draft planning/BE_PLAN.md and start backend implementation only if TASK.md phase is 4_BUILD."
bash scripts/route_to_pane.sh FE "You are FE. Read docs/product/UX_FLOW.md and docs/architecture/API_CONTRACT.md. Draft planning/FE_PLAN.md and start frontend implementation only if TASK.md phase is 4_BUILD."
```

QA to BE/FE:

```bash
bash scripts/route_to_pane.sh BE "QA found backend issues in reports/BUG_REPORT.md. Please fix only backend issues assigned to BE, then report back to QA."
bash scripts/route_to_pane.sh FE "QA found frontend issues in reports/BUG_REPORT.md. Please fix only frontend issues assigned to FE, then report back to QA."
```

Delivery to QA:

```bash
bash scripts/route_to_pane.sh QA "Delivery completed docker build/run. Please run release verification and update reports/TEST_REPORT.md."
```
