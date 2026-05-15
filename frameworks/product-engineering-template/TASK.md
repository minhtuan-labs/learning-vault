# TASK.md — Product Engineering Control Board

## Current Phase
- Phase: 0_DISCOVERY
- Status: IN_PROGRESS
- Owner: ORCHESTRATOR

## Phase Gate Rules
Không chuyển phase nếu chưa có:
- Output file của phase hiện tại
- Review checklist
- Quyết định: proceed / revise / stop

## Phases

### 0_DISCOVERY
Goal: hiểu product idea, scope, target user, assumptions.
Owner: PM + BA
Output:
- docs/product/PRD.md
- docs/business/BUSINESS_REQUIREMENTS.md
- planning/OPEN_QUESTIONS.md

### 1_SOLUTION_DESIGN
Goal: kiến trúc giải pháp, tech stack, system boundary.
Owner: SA
Output:
- docs/architecture/SOLUTION_ARCHITECTURE.md
- docs/architecture/TECH_STACK.md
- docs/architecture/ADR.md

### 2_BACKLOG_AND_SPEC
Goal: user stories, API contract, UX flow, acceptance criteria.
Owner: PM + BA + UX + SA
Output:
- planning/BACKLOG.md
- docs/business/USER_STORIES.md
- docs/product/UX_FLOW.md
- docs/architecture/API_CONTRACT.md

### 3_IMPLEMENTATION_PLANNING
Goal: chia task FE/BE, test plan, delivery plan.
Owner: BE + FE + QA + DELIVERY
Output:
- planning/BE_PLAN.md
- planning/FE_PLAN.md
- docs/qa/TEST_PLAN.md
- docs/delivery/DELIVERY_PLAN.md

### 4_BUILD
Goal: code theo task đã duyệt.
Owner: BE + FE
Output:
- backend/
- frontend/

### 5_TEST_AND_FIX
Goal: test, fix bug, regression.
Owner: QA + BE + FE
Output:
- reports/TEST_REPORT.md
- reports/BUG_REPORT.md

### 6_DELIVERY
Goal: build, run, docker, commit/push nếu pass.
Owner: DELIVERY
Output:
- docker-compose.yml
- docs/delivery/RELEASE_NOTES.md

## Agent Communication Protocol — v10

Mọi agent gửi việc cho agent khác qua tmux pane routing:

```bash
bash scripts/route_to_pane.sh SA "Please review architecture assumptions in docs/architecture/SOLUTION_ARCHITECTURE.md"
```

Phase delegation (chỉ Orchestrator nên gọi):

```bash
bash scripts/delegate_phase.sh <phase>
```

Built-in `Task` / `general-task` subagents bị disabled bởi
`.opencode/config.json` — không agent nào được dùng chúng. Mọi handoff
phải là một lệnh `bash` thật.

Không agent nào tự ý chuyển phase. Orchestrator quyết định phase gate.
