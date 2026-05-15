# Product Engineering Process

## Principle
Product idea nằm trong `PRODUCT_IDEA.md`. Process, role, prompt và task framework nằm trong template này.

## Role Boundary
- PM, SA, BA, UX: không viết production code.
- BE, FE: chỉ code sau khi backlog/spec đã đủ rõ.
- QA: độc lập, không tự sửa code trừ khi được Orchestrator giao.
- DELIVERY: chỉ commit/push sau khi build/run/test pass.

## Decision Flow
User → Orchestrator → đúng agent → output file → review → phase gate → next phase.

## Minimum Viable Governance
1. Mọi thay đổi quan trọng phải được ghi vào `TASK.md`.
2. Mọi quyết định kiến trúc phải được ghi vào `docs/architecture/ADR.md`.
3. Mọi requirement phải có acceptance criteria.
4. Mọi release phải có test report.


## Multi-pane Agent Rule

Each agent has its own pane and its own model. Work must be executed in the pane of the responsible agent.

Agents must not simulate other agents inside their own pane. Use:

```bash
bash scripts/route_to_pane.sh <AGENT> "<message>"
```

or for phase-level delegation:

```bash
bash scripts/delegate_phase.sh <phase>
```


## v9 Pane Routing

This template uses tmux panes as the execution boundary.

Do not use OpenCode internal subagents.

Route work with:

```bash
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

or:

```bash
bash scripts/delegate_phase.sh <phase>
```
