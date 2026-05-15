# Product Engineering Agent Template — v10.12

> A tmux-based, multi-model agent framework for running an entire
> product-engineering team — Orchestrator, PM, SA, BA, UX, BE, FE, QA,
> Delivery — each in its own pane, each on its own LLM, talking to each
> other (and to you) through real shell commands.

**Một template để bạn dựng "đội ngũ kỹ sư sản phẩm AI" trên tmux:** 9 vai
trò, 9 pane, 9 model khác nhau. Bạn chỉ nói chuyện với Orchestrator;
Orchestrator gửi việc qua các pane còn lại bằng `bash`. Không subagent,
không simulate — mỗi pane là một process thật, mỗi role được chạy bởi
một model phù hợp với chi phí và năng lực.

Built on top of a **pluggable CLI engine** — pick one at session start:

- **[OpenCode](https://github.com/sst/opencode)** (`opencode-go` provider) —
  default, multi-provider, fine-grained cost mix; best for newbies and
  experimenters on free / cheap tiers.
- **[Claude Code](https://docs.claude.com/en/docs/claude-code)** (Anthropic) —
  single API key, 3-tier model lineup (Haiku / Sonnet / Opus); best for
  single-vendor production-style use.

Driven by tmux (3-window layout: OC / DESIGN / DEV), glued together with
shell scripts. See [`config/engines/`](config/engines/README.md) for
how to add a third engine (aider, goose, codex, gemini-cli…).

---

## Why this exists

LLM agent frameworks usually run "subagents" inside one process — same
model, same context, same tools. That hides three problems:

1. **You can't price-tune per role.** PM doesn't need GPT-class power;
   BE/SA usually do. With one process you pay the strongest model's
   price for every task.
2. **You can't see the work.** Subagent transcripts get summarized away.
3. **Roles bleed into each other.** A "PM subagent" called from BE often
   ends up writing code anyway.

This template makes each role a **separate tmux pane running a
separate engine session under a separate model**. The Orchestrator
delegates by literally typing `bash scripts/route_to_pane.sh <ROLE>
"<message>"` — which spawns the chosen engine (OpenCode or Claude Code)
in that pane with the right model and the right prompt. You can attach
to any pane and watch the work happen in real time.

---

## Architecture

```text
                    +----------------------------+
                    |          you (user)        |
                    +-------------+--------------+
                                  |
                       chat (tmux window 0, OC)
                                  v
                    +----------------------------+
                    |        ORCHESTRATOR        |
                    |   <engine>/<orch_model>    |
                    |   e.g. opencode-go/glm-5.1 |
                    |        claude-sonnet-4-6   |
                    +-------------+--------------+
                                  |
                bash scripts/route_to_pane.sh <ROLE> "<msg>"
                                  |
       window 1: DESIGN            window 2: DEV
    +----+----+----+----+    +----+----+----+----+
    | PM | SA | BA | UX |    | BE | FE | QA |DEL |
    +----+----+----+----+    +----+----+----+----+

each pane: its own engine process, its own model, its own .pane_logs/<role>_<ts>.log
```

Pane 1 (window 0) runs the chosen engine interactively (auto-relaunched
if it ever exits, so your chat session stays alive). The other 8 panes
in windows 1–2 stay as idle bash workers until `route_to_pane.sh`
(or `delegate_phase.sh`) wakes them with
the engine's non-interactive run command. Every routing call leaves
a receipt in `.pane_logs/_routing_receipts.log` so you can audit what
actually fired vs. what the Orchestrator only described in chat.

Workers can pause mid-task to ask the user a question — see
[Interactive clarifications](#interactive-clarifications) below.

---

## Quick start

```bash
# 1. Clone (or copy) the template into your new project folder
git clone https://github.com/minhtuan-labs/learning-vault.git
cd learning-vault/frameworks/product-engineering-template
cp -R . ~/my-new-project && cd ~/my-new-project
chmod +x scripts/*.sh

# 2. Write a one-pager about what you want to build
$EDITOR PRODUCT_IDEA.md

# 3. Pick an engine and verify models (v10.12)
bash scripts/check_models.sh opencode    # default
# or: bash scripts/check_models.sh claude

# 4. Start the 3-window tmux session
bash scripts/start_agents_tmux.sh my-new-project              # engine=opencode
# or explicit engine:
bash scripts/start_agents_tmux.sh my-new-project --engine claude
```

The engine config file (`.opencode/config.json` for OpenCode,
`.claude/settings.json` for Claude Code) is **auto-generated** at
session start — you don't need to copy or edit it manually.

Engine choice persists in `.agent_session` so subsequent
`route_to_pane.sh` / `answer_role.sh` calls pick the right CLI
automatically. See
[`config/engines/README.md`](config/engines/README.md) for adding
new engines (aider, goose, codex, gemini-cli…).

Then **only talk to pane 1 (Orchestrator)**. Try:

> "Hãy bắt đầu phase discovery"
> "Start the project"
> "Design the architecture"
> "Ask BA to clarify the discount rule"

Orchestrator will execute `bash scripts/delegate_phase.sh discovery` (or
`route_to_pane.sh BA "..."`) and the other panes will fill in their
output files. To prove a real handoff happened:

```bash
bash scripts/verify_routing.sh
```

---

## Roles, models, and outputs

Each role owns a write boundary and runs on a per-role model. Models
differ between engines (configured in `config/engines/<engine>.env`).

| Pane / Window | Role | Owns | Writes |
|---|---|---|---|
| W0 — OC | ORCHESTRATOR | routing, phase gates | `TASK.md`, `memory/_PROJECT_STATE.md` |
| W1 — DESIGN | PM | scope, PRD, roadmap, MVP | `docs/product/PRD.md`, `docs/product/ROADMAP.md`, `planning/BACKLOG.md` |
| W1 — DESIGN | SA | architecture, tech stack, API boundary | `docs/architecture/*.md` |
| W1 — DESIGN | BA | business rules, user stories | `docs/business/*.md` |
| W1 — DESIGN | UX | UX flow, wireframes | `docs/product/UX_FLOW.md`, `docs/product/WIREFRAMES.md`, `docs/product/DESIGN_NOTES.md` |
| W2 — DEV | BE | backend code & tests | `backend/`, `planning/BE_PLAN.md` |
| W2 — DEV | FE | frontend code & tests | `frontend/`, `planning/FE_PLAN.md` |
| W2 — DEV | QA | test plan, test execution, release gate | `docs/qa/*.md`, `reports/*.md` |
| W2 — DEV | DELIVERY | Docker, deploy, release notes | `Dockerfile`, `docker-compose.yml`, `docs/delivery/*.md` |

### Default model per role — per engine

The framework ships defaults for both engines. Override in
`config/engines/<engine>.env`.

| Role | OpenCode (`opencode-go/…`) | Claude Code | Why this model |
|---|---|---|---|
| ORCHESTRATOR | `glm-5.1` | `sonnet-4-6` | **Balanced router** — talks every user turn, needs decent reasoning to dispatch correctly + cost-efficient because used most. |
| PM           | `deepseek-v4-flash` | `haiku-4-5` | **Templated planning** — PRD, roadmap, backlog are structured docs. Fast/cheap tier is plenty. |
| SA           | `deepseek-v4-pro`   | `opus-4-6`   | **High stakes, hard to reverse** — architecture + tech stack choices echo through every later phase. Wrong call = expensive rework, so invest in the strongest tier. |
| BA           | `qwen3.6-plus`      | `haiku-4-5`  | **Rule extraction** — user stories + Given-When-Then ACs are pattern-driven, cheap tier handles them well. |
| UX           | `mimo-v2.5`         | `haiku-4-5`  | **Pattern-following** — UX flows/wireframes draw on well-known interaction patterns. `mimo-v2.5` is OpenCode's multimodal-leaning option. |
| BE           | `deepseek-v4-pro`   | `opus-4-6`   | **Code correctness matters** — backend logic, schemas, auth, transactions. Bugs are expensive; pay for the strong tier same as SA. |
| FE           | `kimi-k2.6`         | `sonnet-4-6` | **Code aesthetics + UI logic** — simpler than backend business logic but still wants good code quality. Balanced tier; `kimi-k2.6` has a good code-gen reputation. |
| QA           | `qwen3.5-plus`      | `haiku-4-5`  | **Structured test work** — test plan, test cases, parsing test output, writing `VERDICT: PASS/FAIL`. Cheap tier is enough. |
| DELIVERY     | `glm-5`             | `haiku-4-5`  | **Highly templated** — Dockerfile/compose patterns, env handling, release notes. Cheap tier; `glm-5` is solid for scripting. |

The defaults mix "strong / medium / cheap" tiers to keep cost down —
PM/BA/UX/QA/DELIVERY don't need expensive models, SA/BE/FE do, and
the ORCHESTRATOR sits in the middle because it's invoked on every
single user turn (cost per turn matters more than raw power).

---

## Cross-session memory (resume the next day)

Workers run one-shot (e.g. `opencode run … "<task>"` or
`claude --print … "<task>"`) and exit each time. Without an explicit
memory layer, every task would start from scratch — the team would
forget decisions made yesterday. v10.5 adds a `memory/` directory
that is **committed to git** and acts as the team's durable
scratchpad.

```text
memory/
├── README.md                ← format guide + discipline
├── _PROJECT_STATE.md        ← team snapshot (Orchestrator owns)
├── ORCHESTRATOR.md          ← routing decisions
├── PM.md  SA.md  BA.md      ← per-role decisions / conventions /
├── UX.md  BE.md  FE.md         gotchas / open items
├── QA.md  DELIVERY.md
```

Each role's prompt mandates two things:

1. **Read at start of every task** — `memory/_PROJECT_STATE.md` plus
   `memory/<ROLE>.md`. These hold the connective tissue: "I chose
   Postgres because user said free Supabase tier" / "FE uses host
   port 3001 on macOS because 3000 conflicts with AirTunes".
2. **Append at end of every task** — a dated entry to
   `memory/<ROLE>.md`. Even routine tasks get a one-line "no new
   entries" stub so the slot isn't silently skipped.

`scripts/route_to_pane.sh` and `scripts/answer_role.sh` embed these
instructions into every task file, so workers can't easily forget.
The Orchestrator additionally updates `memory/_PROJECT_STATE.md`
(current phase, active workstreams, pending questions, last deploy
URL) after every phase delegation.

### Session resume

When you re-run `bash scripts/start_agents_tmux.sh <project>` the
next day, the framework checks `memory/` and `docs/` for substantive
content. If found:

- Prints `[v10.5] RESUME mode — <reason>`
- Writes `AGENT_SESSION_MODE=RESUME` into pane 1's env
- Auto-pings the Orchestrator TUI with a `[RESUME]` kickoff message
  a few seconds after the engine loads

The Orchestrator's first action then is:

```bash
bash scripts/rescan_project.sh
```

…which prints a single consolidated snapshot:

```text
- Last known project state (memory/_PROJECT_STATE.md)
- Recent entries from each role's memory file
- Docs with substantive content
- backend/ and frontend/ source-code presence
- Docker artefacts present / missing
- Last deployed URL (docs/delivery/RUNNING_APP.md)
- Open clarifications + pending notifications
```

The Orchestrator summarises this for you in 3-5 bullets and **waits
for direction** — it never auto-restarts a phase you already shipped.

If memory ever drifts from actual file state, run
`bash scripts/rescan_project.sh` yourself — it's safe to run any
time, just prints, never changes anything.

---

## Interactive clarifications

Real product work is full of "wait, which option do you actually want?"
moments — tech stack, business rules, design preferences, scope cuts.
This template makes those decisions go to **you** (the user), routed
through the Orchestrator.

### How it works

```text
SA needs a decision the spec didn't cover
   │
   │  bash scripts/ask_orchestrator.sh SA "Postgres or MongoDB for primary store?"
   ▼
.pane_questions/SA_20260514_080000.md   ← question saved
   │
   │  Orchestrator: bash scripts/list_pending_questions.sh
   ▼
Orchestrator shows you the question in chat
   │
   │  you reply: "Postgres please, free Supabase tier"
   ▼
Orchestrator: bash scripts/answer_role.sh SA SA_20260514_080000 "Postgres on Supabase free tier"
   │
   ▼
.pane_answers/SA_20260514_080000.md     ← answer saved
+ SA pane automatically resumes with the answer attached
```

### Every role can ask, not just SA

The "stop and ask" rule is universal. PM stops on MVP scope cuts. SA
stops on tech stack. BA stops on conflicting business rules. UX stops
on accessibility level. BE/FE stop on framework or data-store choices.
QA stops on coverage thresholds. DELIVERY stops on deployment target.
Each role's prompt (`prompts/agents/<ROLE>.md`) lists role-specific
triggers; the universal threshold lives in `AGENTS.md`.

The intent is simple: anything that locks the project into a vendor,
changes user-visible behavior, or where the user would plausibly say
"that's not what I wanted" — go ask, don't guess.

### Commands cheat sheet

```bash
# (worker, mid-task)
bash scripts/ask_orchestrator.sh <ROLE> "<question>"

# (Orchestrator, every user turn)
bash scripts/list_pending_questions.sh

# (Orchestrator, after the user answers)
bash scripts/answer_role.sh <ROLE> <question_id> "<the user's answer>"
```

`answer_role.sh` internally calls `route_to_pane.sh` to resume the role,
so the Orchestrator does not need a separate route call.

---

## Workflow (phase gates)

The Orchestrator advances the project through 7 phases. You can also
ask it to skip ahead, but each phase produces concrete output files
before the next one starts.

```text
0_DISCOVERY     -> PM + BA + UX     -> PRD, BUSINESS_REQUIREMENTS, UX_FLOW
1_SOLUTION      -> SA               -> SOLUTION_ARCHITECTURE, TECH_STACK, ADR
2_BACKLOG       -> PM + BA + UX + SA -> BACKLOG, USER_STORIES, API_CONTRACT
3_PLANNING      -> BE + FE + QA + DEL -> BE_PLAN, FE_PLAN, TEST_PLAN, DELIVERY_PLAN
4_BUILD         -> BE + FE          -> backend/, frontend/
5_TEST_AND_FIX  -> QA + BE + FE     -> TEST_REPORT, BUG_REPORT
6_DELIVERY      -> DELIVERY         -> RELEASE_NOTES, docker-compose.yml
```

Phase shortcut:

```bash
bash scripts/delegate_phase.sh discovery   # fans out to PM, BA, UX
bash scripts/delegate_phase.sh solution    # SA
bash scripts/delegate_phase.sh backlog     # PM + BA + UX + SA
bash scripts/delegate_phase.sh planning    # BE + FE + QA + DELIVERY
bash scripts/delegate_phase.sh build       # BE + FE
bash scripts/delegate_phase.sh test        # QA — on PASS, auto-routes DELIVERY
bash scripts/delegate_phase.sh delivery    # DELIVERY — Docker build + up + URL
bash scripts/delegate_phase.sh release     # shortcut: test, then deploy if PASS
```

## Release pipeline (the deploy gate)

The path from "code is written" to "I can open this in a browser"
is wired end-to-end:

```text
[user]  "ship it" / "release" / "test the build"
   │
   ▼
[Orchestrator]  bash scripts/delegate_phase.sh release
   │
   ▼
[QA pane]
   • runs actual tests (pytest / vitest / jest / docker probes)
   • captures real stdout into reports/TEST_REPORT.md
   • writes VERDICT: PASS  or  VERDICT: FAIL  on the first line
   │
   ├── on FAIL → bug report + route BE/FE + notify Orchestrator → DELIVERY does NOT run
   │
   └── on PASS → notify_orchestrator + route_to_pane.sh DELIVERY
                 │
                 ▼
              [DELIVERY pane]
                 • parses TEST_REPORT.md (must be VERDICT: PASS — otherwise abort)
                 • if no docker-compose.yml: ask_orchestrator.sh about host ports
                 • writes backend/Dockerfile, frontend/Dockerfile, docker-compose.yml,
                   .env.example  (multi-stage builds, healthchecks, depends_on)
                 • docker compose build  →  docker compose up --build -d
                 • probes:  curl localhost:<FE_PORT>/  and  curl localhost:<BE_PORT>/health
                 • writes docs/delivery/RUNNING_APP.md with the URL
                 • notify_orchestrator.sh DELIVERY "App is live at http://localhost:3000"
                 │
                 ▼
              [Orchestrator]  shows the URL on the user's next turn
```

The verdict is a hard gate: nothing deploys until QA writes
`VERDICT: PASS`. DELIVERY also asks you about host ports the first
time it writes `docker-compose.yml` (sensible defaults: FE=3000,
BE=8000, DB=5432) — you can just say "ok" or override.

To get the live URL at any time:

```bash
cat docs/delivery/RUNNING_APP.md     # or ask the Orchestrator
```

---

## The first-action rule (why this isn't just prompt engineering)

Older versions of the template tried to disable the engine's built-in
`Task` subagent through prompt warnings ("don't use subagents…"). It
didn't work — weak models ignore negative instructions, and the engine
launched with the subagent tool still enabled.

v10 fixes it at three layers:

1. **Config.** `.opencode/config.json` disables the subagent tool via
   the correct schema (`agent.<mode>.tools.task = false`).
2. **Instructions.** `AGENTS.md` is auto-loaded at startup with the
   *positive* rule: "your VERY FIRST tool call must be `bash …`",
   plus a literal input→command mapping.
3. **Audit.** `scripts/verify_routing.sh` checks that real shell
   commands ran. If the Orchestrator only described routing in chat,
   verification fails immediately.

If you see something like "I will assign General Task — PM …" appear in
the Orchestrator pane, the framework is broken — file an issue.

---

## Project layout

```text
.
├── AGENTS.md                       engine auto-loads this (role rules)
├── PRODUCT_IDEA.md                 YOU write this — what to build
├── PRODUCT_ENGINEERING.md          governance rules
├── TASK.md                         current phase + status (Orchestrator owns)
├── README.md                       you're reading it
├── VERSION.md                      changelog
│
├── .opencode/
│   └── config.json                 disables built-in Task tool
├── opencode.json                   mirror of above, for fork compatibility
│
├── config/
│   ├── engines/                    pluggable engine layer (v10.12)
│   │   ├── opencode.env            OpenCode binary + 9 model IDs
│   │   ├── claude.env              Claude Code binary + 9 model IDs
│   │   └── README.md               how to add an engine
│   ├── agent_models.env            (legacy, replaced by engines/opencode.env)
│   ├── opencode.env                runtime flags
│   └── OPENCODE_PERMISSION_POLICY.md
│
├── planning/
│   ├── AGENT_WORKFLOW.md
│   ├── PANE_ROUTING_RULES.md
│   ├── ORCHESTRATOR_RUNTIME_RULES.md
│   ├── BACKLOG.md      OPEN_QUESTIONS.md
│   └── BE_PLAN.md      FE_PLAN.md     (filled in by BE/FE during planning)
│
├── memory/                         durable cross-session memory (committed)
│   ├── README.md                   format + discipline
│   ├── _PROJECT_STATE.md           team snapshot (Orchestrator owns)
│   └── <ROLE>.md                   per-role decisions/conventions/gotchas
│
├── prompts/agents/                 per-role system prompts (9 files)
│
├── docs/
│   ├── product/        (PRD, ROADMAP, UX_FLOW, WIREFRAMES, DESIGN_NOTES)
│   ├── business/       (BUSINESS_REQUIREMENTS, USER_STORIES, DOMAIN_MODEL)
│   ├── architecture/   (SOLUTION_ARCHITECTURE, TECH_STACK, ADR, API_CONTRACT)
│   ├── qa/             (TEST_PLAN, TEST_CASES)
│   └── delivery/       (DELIVERY_PLAN, RELEASE_NOTES, TMUX_USAGE, OPENCODE_SETUP)
│
└── scripts/
    ├── start_agents_tmux.sh        bring up the 9-pane session
    ├── route_to_pane.sh            Orchestrator -> worker pane
    ├── delegate_phase.sh           fan out a whole phase ('release' included)
    ├── rescan_project.sh           "where did we leave off?" snapshot
    ├── check_prerequisites.sh      per-role upstream-input gate
    ├── check_phase_gate.sh         phase exit-criteria check
    ├── advance_phase.sh            officially advance (refuses if gate fails)
    ├── ask_orchestrator.sh         worker -> user (clarification question)
    ├── notify_orchestrator.sh      worker -> user (one-way status event)
    ├── list_pending_questions.sh   Orchestrator inbox (Qs + notifications)
    ├── answer_role.sh              user answer -> worker (auto-resume)
    ├── verify_routing.sh           audit that routing really fired
    ├── inject_boot_prompt.sh       paste a role prompt manually
    ├── run_agent_task.sh           run a task file in the foreground
    ├── check_models.sh             engine-aware model validator
    ├── check_opencode_models.sh    legacy alias → check_models.sh opencode
    ├── bootstrap_docs.sh           create the docs/ skeleton
    ├── agent_banner.sh             pretty banner per pane
    ├── agent_boot_prompt.sh        generates role boot prompts
    └── send_agent.sh               compat alias -> route_to_pane.sh
```

---

## Troubleshooting

**Pane 1 keeps showing "opencode exited — Press Enter to relaunch"** —
that's intentional. v10.2 wraps the Orchestrator in an auto-relaunch
loop so a crash never drops you to bash. Press Enter and you're back
in chat with the previous engine model. If you really do want a
shell, press Ctrl+C or Ctrl+D at that prompt.

**Pane 1 stuck at `dquote>`** — the engine in pane 1 exited *and* something
got pasted into the raw shell before the relaunch wrapper could catch
it (rare in v10.2). Press **Ctrl+C**, then the auto-relaunch loop
should re-prompt you to press Enter.

**Worker pane never reacted to a routed task** — verify the routing
fired:

```bash
bash scripts/verify_routing.sh
```

If receipts exist but the pane is still idle, try `tmux respawn-pane`
on it or re-run `bash scripts/route_to_pane.sh <ROLE> "<message>"`.

**Orchestrator says it routed but `verify_routing.sh` is empty** — the
Orchestrator only described routing in chat. Remind it of the
first-action rule by pasting `AGENTS.md`, or run:

```bash
bash scripts/inject_boot_prompt.sh ORCHESTRATOR
```

**Worker filed a question and now its pane is idle at bash** — expected
behavior. The worker exits after calling `ask_orchestrator.sh`. Tell
the Orchestrator "có câu hỏi nào đang chờ?" / "any pending questions?"
and answer them; `answer_role.sh` will auto-resume the worker.

**Model not found** — run `bash scripts/check_opencode_models.sh` and
fix `config/agent_models.env` with IDs from `opencode models`.

---

## Customizing

- **Pick engine at session start.** `--engine opencode` (default) or
  `--engine claude`. Persisted in `.agent_session`.
- **Claude Code auth mode — IMPORTANT for cost.** Claude Code can bill
  either via per-token API (env var `ANTHROPIC_API_KEY`) or via your
  Pro/Max **subscription** (OAuth login). Multi-agent workflows can
  burn through API credit fast. If you have Pro/Max:
  - `unset ANTHROPIC_API_KEY` in your shell (also comment out the
    `export` in `~/.zshrc` / `~/.bashrc`)
  - `claude /login` → choose **"Log in with Claude.ai account"**
  - Verify with `claude /status`
  - `start_agents_tmux.sh --engine claude` now refuses to launch if
    `ANTHROPIC_API_KEY` is set (override with `CLAUDE_API_MODE_ACK=1`
    if you really want API billing).
- **Swap models per role within an engine.** Edit
  `config/engines/opencode.env` or `config/engines/claude.env`.
- **Add a new engine** (aider, goose, codex, gemini-cli…). Copy one
  of the existing `config/engines/*.env` to a new filename, fill in
  `ENGINE_BINARY`, `ENGINE_RUN_BASE`, `ENGINE_MODEL_FLAG`, etc., plus
  9 `<ROLE>_MODEL=…`. Then `bash scripts/check_models.sh <new>` to
  validate. Full guide: [`config/engines/README.md`](config/engines/README.md).
- **Swap providers** within an engine (anthropic, openrouter, ollama,
  etc.). For OpenCode, use full IDs like `anthropic/claude-sonnet-4-6`
  in `config/engines/opencode.env` — the framework doesn't care which
  provider, only that each role's model resolves in `opencode models`.
- **Tighten / loosen permissions.** Edit `.opencode/config.json` (for
  OpenCode) or `.claude/settings.json` (for Claude Code — auto-generated
  at session start, edit the generator in `scripts/start_agents_tmux.sh`
  if needed). Both engines have the built-in `Task` subagent
  hard-disabled by default.
- **Add a new role.** Add it to `AGENTS=(...)` in
  `scripts/start_agents_tmux.sh`, drop a `prompts/agents/<NAME>.md`,
  set `<NAME>_MODEL=…` in BOTH `config/engines/opencode.env` and
  `config/engines/claude.env` (or whichever engines you use), and
  reference the role in `planning/AGENT_WORKFLOW.md`.

---

## Version history

See [`VERSION.md`](VERSION.md) for the full changelog. Most recent
fixes:

- **v10.12** — **Engine choice** (OpenCode or Claude Code) + **3-window
  tmux layout** (OC / DESIGN / DEV). `--engine claude` adds Anthropic
  Claude Code as an alternative to `opencode-go` — backward-compatible
  default is `opencode`. Window 0 hosts Orchestrator full-size; window
  1 (DESIGN) tiles PM/SA/BA/UX; window 2 (DEV) tiles BE/FE/QA/DELIVERY.
  Purely additive — all v10.0–v10.11 rules preserved.
- **v10.11** — **Framework files marked immutable** + **safe sync
  script**. New `scripts/sync_framework_from_template.sh` upgrades
  the framework on a running project without clobbering the team's
  work (backs up overwrites to `.framework_sync_backup/`). AGENTS.md
  now explicitly forbids agents from editing AGENTS.md, prompts/,
  scripts/, config/, .opencode/, etc. — only `TASK.md` and `memory/`
  are mutable project state. Purely additive.
- **v10.10** — **Stay-in-lane** rule + **Build Failure Routing
  Protocol**. DELIVERY hitting a `docker compose build` failure now
  routes BE / FE / SA-to-triage and exits — it cannot read or edit
  `backend/`/`frontend/` source. SA gets a Triage Protocol for
  picking the owner from the architecture docs. Universal write-
  boundary table in AGENTS.md so every role knows what it owns and
  what it must hand off. Purely additive.
- **v10.9** — **Phase gates with quality enforcement**. New
  `check_phase_gate.sh` and `advance_phase.sh` enforce the real
  product-engineering process: can't enter phase N until phase N-1
  passes its exit criteria. DELIVERY's prereq now hard-blocks
  release unless TEST_REPORT says `VERDICT: PASS`, BUG_REPORT has
  no `OPEN_CRITICAL`/`OPEN_MAJOR`/`RETEST_FAIL`, TECH_STACK is
  "Confirmed by user", AND real source files exist in `backend/` &
  `frontend/`. Documented bug-status vocabulary in QA prompt for
  parseable release-gate input. Purely additive.
- **v10.8** — **Prerequisite check** before any work. New
  `scripts/check_prerequisites.sh <ROLE>` defines per-role upstream
  inputs (e.g. BE needs `SOLUTION_ARCHITECTURE`, `API_CONTRACT`,
  `TECH_STACK`, `USER_STORIES`). If any is missing or skeleton-only,
  the worker exits with a `notify_orchestrator.sh` listing missing
  files and their upstream owners — Orchestrator then coordinates
  the upstream agents to produce them first and re-routes the
  blocked worker. Closes the hole where agents silently invented
  placeholder content for files another role owned. Purely additive.
- **v10.7** — **Tech Stack Confirmation Protocol**. SA (and BE/FE
  for second-order picks) must run `ask_orchestrator.sh` with a
  batched proposal covering FE framework, BE framework, language,
  datastore, ORM, auth, UI system, hosting, code layout, package
  manager BEFORE writing `docs/architecture/TECH_STACK.md`. Closes
  the v10.3 hole where SA silently rubber-stamped Next.js / React /
  Postgres "obvious defaults". Purely additive — all v10.0–v10.6
  rules preserved.
- **v10.6** — Lean role-specific read list in every task file.
  `route_to_pane.sh` now emits a tailored "must-read" list per
  target role (annotated with file existence / size) plus an
  explicit "do NOT read by default" block. Cuts per-task read
  overhead by ~50% on top of v10.5's memory layer.
- **v10.5** — Durable `memory/` layer (committed to git) so the
  team can pick up where it left off the next day. Every worker
  reads `memory/<ROLE>.md` + `memory/_PROJECT_STATE.md` at start of
  task, appends a dated entry at end. `start_agents_tmux.sh` detects
  RESUME vs FRESH; on RESUME the Orchestrator auto-runs
  `rescan_project.sh` and recaps progress instead of re-running
  finished phases. New script `scripts/rescan_project.sh` prints a
  consolidated "where are we?" snapshot.
- **v10.4** — Auto-wake the Orchestrator when a worker files a
  question or notification (`ask_orchestrator.sh` /
  `notify_orchestrator.sh` now inject an `[INBOX]` one-liner into the
  Orchestrator's TUI and press Enter). Before this fix, blocked
  workers would sit idle until the user happened to ask "có gì
  pending?" — even though three roles might have been waiting at once.
- **v10.3** — QA actually runs the test suite and emits a
  `VERDICT: PASS / FAIL` line that DELIVERY parses as a release gate.
  DELIVERY now ships end-to-end: asks for host ports, writes
  Dockerfiles + `docker-compose.yml`, runs `docker compose up
  --build -d`, probes endpoints, writes `docs/delivery/RUNNING_APP.md`
  with the live URL, and notifies the Orchestrator so the user gets
  the URL on their next turn. New `notify_orchestrator.sh` for
  one-way events; `release` phase chains test→deploy.
- **v10.2** — two-way clarification loop (`ask_orchestrator.sh`,
  `list_pending_questions.sh`, `answer_role.sh`). Orchestrator pane
  auto-relaunches on exit instead of dropping to bash.
  `route_to_pane.sh` refuses `ORCHESTRATOR` to prevent self-routing
  from killing the user's chat session. Stop-and-ask threshold + per-
  role example triggers added to all 8 worker prompts.
- **v10.1** — drop `--config` CLI flag (opencode-go rejects it),
  switch to AGENTS.md for role instructions, kill the racy boot-prompt
  auto-paste that left pane 1 stuck at `dquote>`.
- **v10.0** — actually disable the built-in `Task` subagent (correct
  schema + real config file). Add `verify_routing.sh`. Rewrite
  Orchestrator prompts to be action-first.
- **v9** — first attempt at permission-based subagent blocking
  (silently ignored by OpenCode — see VERSION.md for the post-mortem).

---

## Contributing

This is a personal hobby project. PRs, issues, and ideas are welcome —
especially if you've tried it with a different engine fork or model
provider and hit something the template assumes about `opencode-go`.

If you're trying it on a project of your own, I'd love to hear what
worked and what didn't.

---

## License

MIT — see [`LICENSE`](LICENSE). Use it however you like.

Built by [Tuan M. Pham](https://github.com/) for fun and to stop paying
for one strong model to do nine different jobs.
