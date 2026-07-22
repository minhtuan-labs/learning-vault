# TMUX Usage — v10.24

> **What's new since v10.12** (see `VERSION.md`):
>
> - **v10.21 Banner shows PaneC + display names**: the pane banner
>   now lists `AGENT:` (internal ID), `DISPLAY:` (conversational
>   name — Orches / Deli / etc.), and `TEAM: PaneC (9-pane crew)`.
> - **v10.23 Write/Edit hook** — Orchestrator pane has a PreToolUse
>   hook registered in `.claude/settings.json` that rejects
>   Write/Edit on owner-specific paths. Worker panes unaffected.
>
> - **Prefix + W** (v10.18): manual wake nudge for the Orchestrator
>   pane via `scripts/wake_orchestrator.sh`. Useful when auto-wake
>   misses on Claude. Types `.` + Enter into pane 0 to trigger the
>   mandatory turn-start inbox check.
> - **`bash scripts/stop_agents_tmux.sh`** (v10.18): clean shutdown
>   that kills the watcher_daemon (via `.watcher.pid`) before
>   `tmux kill-session`. Use this instead of bare `tmux kill-session`
>   so the background daemon doesn't orphan.
> - **PATH guards** (v10.19): the Orchestrator pane runs with
>   `scripts/guards/` prepended to PATH. Worker panes don't. Means
>   `docker`/`psql`/`python`/`npm`/etc. in the Orchestrator pane
>   prints `BLOCKED — Orchestrator cannot execute engineering
>   commands` and exits 126. Worker panes use real binaries.


## Start

```bash
bash scripts/start_agents_tmux.sh <project_name>                    # default: opencode
bash scripts/start_agents_tmux.sh <project_name> --engine opencode
bash scripts/start_agents_tmux.sh <project_name> --engine claude
```

This regenerates the engine config (`.opencode/config.json` or
`.claude/settings.json`), validates models, then opens **3 tmux windows**:

```text
Window 0 — OC       (1 pane)     ORCHESTRATOR — your interactive chat session
Window 1 — DESIGN   (2×2 panes)  PM, SA, BA, UX  (planning roles)
Window 2 — DEV      (2×2 panes)  BE, FE, QA, DELIVERY  (implementation roles)
```

Switch between windows: `Ctrl+B 0`, `Ctrl+B 1`, `Ctrl+B 2`.

The status bar shows `[<session> | <engine>]` so you always know which
engine is driving the session.

## Pane behaviour

```text
0:OC                 1:DESIGN                  2:DEV
+-----------------+  +-------+-------+         +-------+-------+
|                 |  |  PM   |  SA   |         |  BE   |  FE   |
| ORCHESTRATOR    |  +-------+-------+         +-------+-------+
| (interactive)   |  |  BA   |  UX   |         |  QA   |  DEL  |
|                 |  +-------+-------+         +-------+-------+
+-----------------+
```

Pane 1 (Orchestrator) runs the engine TUI continuously and
auto-relaunches if it exits. Other panes stay as idle shells until
woken by `scripts/route_to_pane.sh`.

## Correct routing

Phase-level (preferred for "start project", "build it", etc.):

```bash
bash scripts/delegate_phase.sh discovery
```

Custom routing to a specific role:

```bash
bash scripts/route_to_pane.sh SA "You are SA. Read PRODUCT_IDEA.md. Write docs/architecture/SOLUTION_ARCHITECTURE.md."
```

`route_to_pane.sh` reads `ENGINE=` from `.agent_session` and dispatches
the correct CLI (`opencode run --model …` or `claude --print --model
…`) based on the active engine.

## What happens under the hood

`route_to_pane.sh` writes a task file to `.pane_tasks/` and then, in
the target pane, runs:

```bash
# When engine=opencode:
OPENCODE_CONFIG=<project>/.opencode/config.json \
  opencode run --model <target_pane_model> \
    "Execute the routed pane task ..."

# When engine=claude:
claude --print --model <target_pane_model> \
    "Execute the routed pane task ..."
```

A routing receipt is appended to `.pane_logs/_routing_receipts.log` so
the routing event is auditable regardless of engine.

## Verify routing

```bash
bash scripts/verify_routing.sh
```

If this prints "no routing has fired" right after Orchestrator told you
it routed work, the bug is back — Orchestrator is only describing the
delegation instead of running the bash command.

## Files

```text
.opencode/config.json                 (engine=opencode policy)
.claude/settings.json                 (engine=claude policy)
.pane_tasks/                          (one .md per routed task)
.pane_logs/                           (one .log per routed task)
.pane_logs/_routing_receipts.log      (audit log of every routing call)
.agent_panes                          (role -> tmux pane id, unique per session)
.agent_session                        (ENGINE, SESSION_NAME, PROJECT_DIR)
```

## Avoid

Do not rely on the engine's internal subagents (`Task`, `General
Task`, `general-task`). They are disabled at the config level for both
engines in v10.12. If you ever see one offered in another fork, do not
use it — the multi-pane design depends on real shell handoff.
