# `config/engines/` — pluggable engine layer (v10.12)

The framework supports more than one underlying AI coding CLI ("engine").
This directory contains one file per supported engine plus this guide.

```
config/engines/
├── opencode.env     ← OpenCode (opencode-go fork) — default
├── claude.env       ← Anthropic Claude Code
└── README.md        ← you are here
```

## How engine selection works

```bash
# Default (opencode)
$ bash scripts/start_agents_tmux.sh my-project

# Explicit
$ bash scripts/start_agents_tmux.sh my-project --engine opencode
$ bash scripts/start_agents_tmux.sh my-project --engine claude
```

`start_agents_tmux.sh`:

1. Parses `--engine <name>`, sources `config/engines/<name>.env`.
2. Validates the engine binary exists and every role's model is reachable
   (`scripts/check_models.sh` dispatches based on `ENGINE_MODEL_CHECK_MODE`).
3. Writes `ENGINE=<name>` into `.agent_session` so every later script knows
   which engine to dispatch.

`route_to_pane.sh`, `run_agent_task.sh`, `answer_role.sh` then re-source
`config/engines/${ENGINE}.env` and build commands using `$ENGINE_BINARY`,
`$ENGINE_RUN_BASE`, `$ENGINE_MODEL_FLAG`, etc.

## What each engine env must define

| Variable | Purpose |
|---|---|
| `ENGINE_NAME` | Short identifier (`opencode`, `claude`, …) |
| `ENGINE_BINARY` | CLI command name (must be in `$PATH`) |
| `ENGINE_TUI_LAUNCH` | How to start interactive TUI (model flag added by scripts) |
| `ENGINE_RUN_BASE` | How to do a non-interactive one-shot run |
| `ENGINE_MODEL_FLAG` | CLI flag that selects model (usually `--model`) |
| `ENGINE_CONFIG_ENV_VAR` | If non-empty, scripts export this env var = path to config file |
| `ENGINE_CONFIG_PATH` | Project-local config file the engine reads |
| `ENGINE_AUTO_CONTEXT_FILE` | Markdown file the engine auto-loads at startup |
| `ENGINE_MODEL_CHECK_MODE` | `dynamic` (engine has `models` subcommand) or `static` (whitelist) |
| `ENGINE_MODELS_LIST_CMD` | Used when `MODE=dynamic` — shell command that prints available models |
| `ENGINE_KNOWN_MODELS` | Used when `MODE=static` — space-separated list of valid model IDs |
| `<ROLE>_MODEL` for each of 9 roles | Per-role model ID, must be valid for this engine |

## Choosing an engine

| Aspect | OpenCode | Claude Code |
|---|---|---|
| Cost optimisation | Fine-grained — 7 tiers across providers | Coarser — 3 tiers (haiku/sonnet/opus) |
| Provider dependency | Multi-provider | Anthropic API only |
| Setup | Provider config + opencode binary | Single Anthropic API key |
| Maturity in this framework | Battle-tested v10.0–v10.11 | New as of v10.12 |
| Suggested for | Newbies, free-tier mix, experimenters | Pros, single-vendor setups, single API key |

You can switch engines between sessions; `memory/` is committed to git so
state persists regardless of engine choice.

## Adding a new engine

1. Copy one of the existing `.env` files to
   `config/engines/<new_name>.env`.
2. Fill in the variables above for your CLI.
3. If your engine needs a project-local config file, place a template at
   the path you set in `ENGINE_CONFIG_PATH` (e.g. `.<engine>/config.json`).
4. If your engine auto-loads a context file with a different name, point
   `ENGINE_AUTO_CONTEXT_FILE` at it; `start_agents_tmux.sh` will copy
   `AGENTS.md` to that filename so the rules transfer.
5. Test:

```bash
$ bash scripts/check_models.sh <new_name>
$ bash scripts/start_agents_tmux.sh test-project --engine <new_name>
```

If everything passes, send a PR — we'd love to support aider, goose,
codex, gemini-cli, etc. once we can verify them.
