# Agent Model Mapping — v6

Version 6 uses the validated OpenCode Go provider IDs:

```text
opencode-go/<model-id>
```

## Default mapping

| Agent | Full model ID | Intended role |
|---|---|---|
| ORCHESTRATOR | `opencode-go/glm-5.1` | workflow control and delegation |
| PM | `opencode-go/deepseek-v4-flash` | product scope, PRD, roadmap |
| SA | `opencode-go/deepseek-v4-pro` | solution architecture and API boundaries |
| BA | `opencode-go/qwen3.6-plus` | business rules, user stories, acceptance criteria |
| UX | `opencode-go/mimo-v2.5` | UX flow, wireframes, design notes |
| BE | `opencode-go/deepseek-v4-pro` | backend implementation and backend tests |
| FE | `opencode-go/kimi-k2.6` | frontend implementation and frontend tests |
| QA | `opencode-go/qwen3.5-plus` | test plan, test cases, test report |
| DELIVERY | `opencode-go/glm-5` | Docker, build/run, git, release checklist |

## Validation

Run:

```bash
bash scripts/check_opencode_models.sh
```

If any model fails, inspect exact IDs:

```bash
opencode models
opencode models opencode-go
```
