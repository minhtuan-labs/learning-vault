# TMUX Usage — v10

## Start

```bash
bash scripts/start_agents_tmux.sh <project_name>
```

This regenerates `.opencode/config.json` (the file that actually
disables the built-in Task subagent) and then opens 9 tmux panes.

## Pane behavior

```text
1-ORCHESTRATOR : interactive OpenCode (the one you talk to)
2-PM           : shell worker
3-SA           : shell worker
4-BA           : shell worker
5-UX           : shell worker
6-BE           : shell worker
7-FE           : shell worker
8-QA           : shell worker
9-DELIVERY     : shell worker
```

## Correct routing

Phase-level (preferred for "start project", "build it", etc.):

```bash
bash scripts/delegate_phase.sh discovery
```

Custom:

```bash
bash scripts/route_to_pane.sh SA "You are SA. Read PRODUCT_IDEA.md. Write docs/architecture/SOLUTION_ARCHITECTURE.md."
```

## What happens under the hood

`route_to_pane.sh` writes a task file to `.pane_tasks/` and then, in the
target pane, runs:

```bash
OPENCODE_CONFIG=<project>/.opencode/config.json \
  opencode run \
    --config <project>/.opencode/config.json \
    --model <target_pane_model> \
    "Execute the routed pane task ..."
```

A routing receipt is appended to `.pane_logs/_routing_receipts.log` so
the routing event is auditable.

## Verify routing

```bash
bash scripts/verify_routing.sh
```

If this prints "no routing has fired" right after Orchestrator told you
it routed work, the bug is back — Orchestrator is only describing the
delegation instead of running the bash command.

## Files

```text
.opencode/config.json                 (loaded by OpenCode at startup)
.pane_tasks/                          (one .md per routed task)
.pane_logs/                           (one .log per routed task)
.pane_logs/_routing_receipts.log      (audit log of every routing call)
.agent_panes                          (role -> tmux pane id)
.agent_session                        (session metadata)
```

## Avoid

Do not rely on OpenCode internal subagents (`Task`, `General Task`,
`general-task`). They are disabled at the config level in v10, but if
you ever see one offered in another fork of OpenCode, do not use it —
the multi-pane design depends on real shell handoff.
