# Pane Routing Rules — v10

## Hard rule

This project uses tmux panes — not the engine's internal subagents — as the
execution boundary. The built-in `Task` / `general-task` subagent tool is
disabled at the engine's config level (see
`config/OPENCODE_PERMISSION_POLICY.md`, `.opencode/config.json` for
OpenCode, or `.claude/settings.json` for Claude Code).

## Required routing command

```bash
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

Examples:

```bash
bash scripts/route_to_pane.sh PM "You are PM. Read PRODUCT_IDEA.md. Write docs/product/PRD.md."
bash scripts/route_to_pane.sh SA "You are SA. Read docs/product/PRD.md. Write docs/architecture/SOLUTION_ARCHITECTURE.md."
```

## Phase routing

```bash
bash scripts/delegate_phase.sh discovery
bash scripts/delegate_phase.sh solution
bash scripts/delegate_phase.sh backlog
bash scripts/delegate_phase.sh planning
bash scripts/delegate_phase.sh build
bash scripts/delegate_phase.sh test
bash scripts/delegate_phase.sh delivery
```

## Verify

```bash
bash scripts/verify_routing.sh
```

If this prints "no routing has fired", the Orchestrator only described
routing in chat — the bash command was never actually executed.

## Why

Each pane has its own configured model (`config/agent_models.env`). If
work runs through an internal subagent inside the Orchestrator pane, the
model separation is lost and the whole multi-agent design collapses into
a single-model chat.
