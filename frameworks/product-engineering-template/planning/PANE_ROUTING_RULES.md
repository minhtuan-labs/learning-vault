# Pane Routing Rules — v10.23

> **What's new since v10.12** (see `VERSION.md` for full changelog):
>
> - **v10.21 PaneC** — the team is named PaneC (the 9-pane crew).
>   Orchestrator's display name is **Orches**, Delivery's is **Deli**.
>   Internal `AGENT_NAME` identifiers stay uppercase (zero breaking
>   change). When user says "PaneC cần X", Orches treats as team-level.
> - **v10.22 Deli port discipline** — `check_port_conflicts.sh` has 4
>   modes (basic / `--exhaustive` / `--suggest` / `--verify`). Deli
>   protocol mandates exhaustive scan before every compose-up and
>   post-deploy `--verify` before writing `RUNNING_APP.md`.
> - **v10.23 Layer-4 hook** — `PreToolUse` hook
>   (`scripts/guards/check_file_lane.sh`) blocks Orchestrator's
>   `Write`/`Edit` tool calls on owner-specific paths. Closes the
>   v10.19 loophole where Claude's native file tools bypassed the
>   PATH guard.
>
> - **v10.14 watcher_daemon**: workers that block on missing deps file
>   a watch via `scripts/file_watch.sh`; the daemon auto-reroutes them
>   when the dependency lands. No user nudge needed.
> - **v10.15/18.1 auto-wake**: `notify_orchestrator.sh` / `ask_orchestrator.sh`
>   reliably surface to both OpenCode and Claude via bracketed paste
>   + verification + visible fallback. Manual nudge: **Prefix + W**.
> - **v10.18 silent-exit safety net**: `route_to_pane.sh` wrapper
>   auto-fires a completion notify if the worker exited without one
>   (dedup'd against any worker-fired notify in the prior 30s).
> - **v10.18 heartbeat**: workers `touch .pane_heartbeats/<ROLE>.beat`
>   every 10s; daemon flags stalled workers after 90s of silence.
> - **v10.19 HARD lane discipline for Orchestrator**: PATH guard at
>   `scripts/guards/` blocks docker/psql/python/npm/etc. from the
>   Orchestrator pane. Bug reports MUST route QA first.
> - **v10.20 DELIVERY Port Configuration Protocol**: DELIVERY runs
>   `scripts/check_port_conflicts.sh` before writing compose, offers
>   user options A (preferred) / B (auto) / C (defaults).


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
