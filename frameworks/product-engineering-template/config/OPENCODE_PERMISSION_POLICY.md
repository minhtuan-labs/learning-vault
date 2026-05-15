# OpenCode Permission Policy — v10

## Purpose

This template uses tmux panes as the real execution boundary. OpenCode's
built-in `Task` / `general-task` subagent must be disabled so that work
is routed to real panes — each with its own model — instead of running
inside the Orchestrator's session.

## Why v9 did not work

v9 tried to pass JSON via an env var named `OPENCODE_CONFIG_CONTENT`.
That env var does not exist in OpenCode, so the policy was silently
ignored and the Task tool stayed enabled.

It also used the key `permission.task.*: "deny"` — `task` is not a
permission key in OpenCode's schema (only `bash`, `edit`, `webfetch`
are), so even if the JSON had been loaded the key would have been a
no-op.

## v10: how the policy is actually applied

1. A real config file is generated at `.opencode/config.json` by
   `scripts/start_agents_tmux.sh`.
2. OpenCode is started with both:
   - `--config <project>/.opencode/config.json`
   - `OPENCODE_CONFIG=<project>/.opencode/config.json`
3. The config disables the subagent tool through the correct schema:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": "allow",
    "edit": "allow",
    "webfetch": "allow"
  },
  "agent": {
    "build": {
      "tools": {
        "task": false,
        "general-task": false
      }
    },
    "plan": {
      "tools": {
        "task": false,
        "general-task": false
      }
    }
  }
}
```

## Route-to-pane rule

Use:

```bash
bash scripts/route_to_pane.sh PM "..."
bash scripts/delegate_phase.sh discovery
```

If you suspect routing did not actually happen, run:

```bash
bash scripts/verify_routing.sh
```

This checks `.pane_tasks/` and `.pane_logs/_routing_receipts.log` for
evidence that a real shell command fired (as opposed to the Orchestrator
just describing routing in chat).
