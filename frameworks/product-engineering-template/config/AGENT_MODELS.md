# Agent Model Mapping — v10.12

The framework supports two CLI engines as of v10.12. Each engine has
its own per-role model configuration file under `config/engines/`.
This document is the human-readable mapping for reference; the
authoritative source for code is `config/engines/<engine>.env`.

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

## Validation

```bash
# Default engine (opencode):
bash scripts/check_models.sh
bash scripts/check_models.sh opencode

# Claude:
bash scripts/check_models.sh claude
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
