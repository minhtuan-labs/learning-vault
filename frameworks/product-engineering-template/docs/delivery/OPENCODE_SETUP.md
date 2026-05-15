# OpenCode Setup — v10

## v10 fix vs v9

v9 tried to disable OpenCode's `Task` subagent via:

- env var `OPENCODE_CONFIG_CONTENT` — **does not exist in OpenCode**
- `permission.task.*: "deny"` — **not a real permission key**

Both were silently ignored, so the Task tool stayed enabled and the
Orchestrator naturally used it instead of running our routing scripts.

v10 uses the supported mechanisms:

- Real config file at `.opencode/config.json` (autoloaded; also passed
  via `--config` and the `OPENCODE_CONFIG=<path>` env var).
- Subagent disabled through the agent-tools schema:
  `agent.<mode>.tools.task = false`.

## The config file (`.opencode/config.json`)

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

## Worker execution

Worker panes run:

```bash
OPENCODE_CONFIG=<project>/.opencode/config.json \
  opencode run \
    --config <project>/.opencode/config.json \
    --model <target_pane_model> \
    "Execute the routed pane task ..."
```

## Orchestrator execution

Only Orchestrator runs interactive OpenCode by default:

```bash
AUTO_START_ORCHESTRATOR=true
AUTO_START_WORKER_AGENTS=false
WORKER_OPENCODE_MODE=run
DENY_INTERNAL_TASK_TOOL=true
```

The first three are read by scripts; the fourth is informational — the
real enforcement happens in `.opencode/config.json`.

## Validate models

```bash
bash scripts/check_opencode_models.sh
```

## Verify a routing event

```bash
bash scripts/verify_routing.sh
```
