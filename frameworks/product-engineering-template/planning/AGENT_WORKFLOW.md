# Agent Workflow and Delegation Protocol — v10

## Runtime

Only Orchestrator runs interactive OpenCode. The other 8 panes stay as
idle shells until `route_to_pane.sh` (or `delegate_phase.sh`) starts
OpenCode in them with that pane's configured model. Every delegated
task therefore runs under the target role's model, not Orchestrator's.

## Strict delegation rule

OpenCode's built-in `Task` / `general-task` subagent tool is disabled by
`.opencode/config.json` (see `config/OPENCODE_PERMISSION_POLICY.md`).
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
OPENCODE_CONFIG=<project>/.opencode/config.json \
  opencode run \
    --config <project>/.opencode/config.json \
    --model <target_agent_model> \
    "<task prompt>"
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
