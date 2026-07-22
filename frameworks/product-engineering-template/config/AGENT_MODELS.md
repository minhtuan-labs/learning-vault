# Agent Model Mapping — v10.24

The framework supports two CLI engines (since v10.12) plus a free-tier
overlay (since v10.16). Each engine has its own per-role model
configuration file under `config/engines/`. This document is the
human-readable mapping for reference; the authoritative source for
code is `config/engines/<engine>.env`.

**Team identity (v10.21)**: the 9 agents are collectively called
**PaneC**. Display names: **Orches** = ORCHESTRATOR, **Deli** =
DELIVERY, the rest keep their two-letter codes. Internal `AGENT_NAME`
env vars stay uppercase (zero breaking change). The mapping below
uses internal identifiers because that's what `config/engines/*.env`
uses.

## Engine A — OpenCode (default)

Source: `config/engines/opencode.env`. Provider format: `opencode-go/<model-id>`.

| Role | Model ID | Intended role |
|---|---|---|
| ORCHESTRATOR | `opencode-go/glm-5.1` | workflow control + delegation |
| PM | `opencode-go/deepseek-v4-flash` | product scope, PRD, roadmap |
| SA | `opencode-go/deepseek-v4-pro` | solution architecture + API boundaries |
| BA | `opencode-go/qwen3.6-plus` | business rules, user stories, AC |
| UX | `opencode-go/mimo-v2.5` | UX flow, wireframes, design notes |
| BE | `opencode-go/deepseek-v4-pro` | backend implementation + tests |
| FE | `opencode-go/kimi-k2.6` | frontend implementation + tests |
| QA | `opencode-go/qwen3.5-plus` | test plan, test cases, test report |
| DELIVERY | `opencode-go/glm-5` | Docker, build/run, release checklist |

Strategy: 7-tier mix across providers (deepseek, qwen, kimi, glm,
mimo). Fine-grained cost optimisation — cheap for low-stakes roles
(PM/BA/UX/QA/DELIVERY), strong for high-stakes (SA/BE/FE) plus a
balanced router (ORCHESTRATOR).

## Engine B — Claude Code

Source: `config/engines/claude.env`. Anthropic CLI, 3-tier lineup.

| Role | Model ID | Intended role |
|---|---|---|
| ORCHESTRATOR | `claude-sonnet-4-6` | balanced router (every turn) |
| PM | `claude-haiku-4-5` | planning, fast & cheap |
| SA | `claude-opus-4-6` | architecture — invest here |
| BA | `claude-haiku-4-5` | business rules; cheap |
| UX | `claude-haiku-4-5` | UX flow; cheap |
| BE | `claude-opus-4-6` | backend code — invest here |
| FE | `claude-sonnet-4-6` | frontend code; balanced |
| QA | `claude-haiku-4-5` | test plan; cheap |
| DELIVERY | `claude-haiku-4-5` | Docker/compose; cheap |

Strategy: coarser-grained, only 3 tiers available — haiku for cheap
roles, sonnet for balanced, opus for strong. Single-vendor setup, one
API key.

## Engine A/B FREE overlay (v10.16+)

Pass `--free` to `start_agents_tmux.sh` to source
`config/engines/<engine>-free.env`, an overlay that forces every role
to a free-tier model. Useful for iterating on the workflow without
burning paid credits.

### `config/engines/opencode-free.env`

Default: `opencode/big-pickle` for all 9 roles (confirmed working in
the opencode-go fork). Override per-session via `OPENCODE_FREE_MODEL=…`
or edit the overlay file. Discovery: `bash scripts/list_free_models.sh`.

### `config/engines/claude-free.env`

All 9 roles → `claude-haiku-4-5`. Claude has no $0 tier; for Pro/Max
subscribers, haiku usage counts against monthly quota, not metered API.

`FREE_MODE` is persisted into `.agent_session` so `route_to_pane.sh`,
`run_agent_task.sh`, and `check_models.sh` all keep using the overlay
on subsequent re-routes.

## Validation

```bash
# Default engine (opencode):
bash scripts/check_models.sh
bash scripts/check_models.sh opencode

# Claude:
bash scripts/check_models.sh claude

# v10.16.2 — <engine>-free shorthand
bash scripts/check_models.sh opencode-free
bash scripts/check_models.sh claude-free
# (equivalent to: bash scripts/check_models.sh <engine> --free)
```

OpenCode uses **dynamic** validation (it calls `opencode models`).
Claude Code uses **static** whitelist validation against
`ENGINE_KNOWN_MODELS` in `config/engines/claude.env` (Claude Code has
no `claude models` subcommand).

If a model fails validation, inspect:

```bash
opencode models             # for OpenCode — lists everything available
opencode models opencode-go # filter by provider
claude --version            # for Claude Code — at minimum verify the binary
```

Then edit `config/engines/<engine>.env` with the exact ID.

## Adding a new engine

See [`config/engines/README.md`](engines/README.md).
