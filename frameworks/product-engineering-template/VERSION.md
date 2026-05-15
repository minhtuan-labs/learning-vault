# Template Version

Version: 10.12.1

## Patch v10.12.1 (over v10.12)

Three regressions / UX issues discovered after v10.12 was tagged.
Purely additive fixes — no behavior removed.

### 1. Auto-wake `[INBOX]` ping silently dropped when engine=claude

`ask_orchestrator.sh` and `notify_orchestrator.sh` checked
`tmux display-message #{pane_current_command}` and only fired the
`tmux send-keys` ping when the foreground process matched
`opencode|node|go|main`. **`claude` was missing from the regex**, so
every clarification / notification filed while engine=claude wrote
its file to `.pane_questions/` or `.pane_notifications/` but never
woke up the Orchestrator. The user had to ask "any pending
questions?" by hand for things to surface.

Fix: replaced regex with a case statement that includes
`opencode|claude|node|go|main|bash|sh|zsh`. `bash` is now also
allowed because the Orchestrator's auto-relaunch loop sits at
`read -r _` between engine runs — sending `[INBOX]` + Enter to that
loop triggers a relaunch with the inbox message as the first user
turn, which is fine.

### 2. Orchestrator must always run `list_pending_questions.sh` at
turn start (auto-wake is best-effort)

`prompts/agents/ORCHESTRATOR.md` now says explicitly: the
`[INBOX]` auto-ping is best-effort (depends on what's running in
pane 1 at the moment a worker fires). The only guarantee that
clarifications + notifications surface is the Orchestrator running
`list_pending_questions.sh` at the **start of every user turn** —
even when no `[INBOX]` is visible, even when the user's message
looks unrelated. Worded as "non-negotiable" to push weaker models
to comply.

### 3. Agents weren't asking proactively beyond Tech Stack

User feedback: "Only SA Tech Stack triggered prompts. Other agents
silently decided." Strengthened `AGENTS.md` Stop-and-ask threshold:

- Added an explicit "DEFAULT TO ASKING — err on the side of asking"
  preamble quoting the user's own words.
- Added a new trigger: "About to write > 50 lines of content/code in
  a direction the user hasn't endorsed → ask first."
- Added a per-role-per-phase checklist of questions that "almost
  always" have legitimate clarifications (PM at Discovery, UX at
  Discovery/Backlog, BE/FE at Planning, QA at Planning, DELIVERY at
  Delivery, etc.).
- Spelled out: "If a role goes through an entire phase without
  filing a single `ask_orchestrator.sh`, that role probably guessed
  silently."

## Changes from v10.11

### 1. Engine choice — pluggable OpenCode / Claude Code

Through v10.11 the framework hard-coded `opencode` as the CLI binary
everywhere (model IDs, config file paths, validation commands, run
syntax). v10.12 abstracts the engine so the user picks at session
start:

```bash
$ bash scripts/start_agents_tmux.sh my-project              # default: opencode
$ bash scripts/start_agents_tmux.sh my-project --engine opencode
$ bash scripts/start_agents_tmux.sh my-project --engine claude
```

New files:

- `config/engines/opencode.env` — per-engine binary, run command,
  config path, auto-context filename, model-validation mode, and 9
  per-role model IDs.
- `config/engines/claude.env` — same, for Claude Code (3-tier mapping:
  Haiku for cheap roles, Sonnet for balanced, Opus for strong).
- `config/engines/README.md` — guide to adding a new engine.
- `CLAUDE.md` — Claude Code's auto-context file. Regenerated from
  `AGENTS.md` whenever `--engine claude` is used.

Modified scripts (engine-aware):

- `scripts/start_agents_tmux.sh` — parses `--engine`, sources
  `config/engines/<name>.env`, validates models per engine's mode
  (dynamic for opencode via `opencode models`; static whitelist for
  claude). Writes `ENGINE=<name>` into `.agent_session`. Generates
  the engine's policy file (`.opencode/config.json` or
  `.claude/settings.json`) inline at startup.
- `scripts/route_to_pane.sh` — reads engine from `.agent_session`,
  dispatches `$ENGINE_RUN_BASE $ENGINE_MODEL_FLAG <model> "<task>"`.
- `scripts/run_agent_task.sh` — same.
- `scripts/check_models.sh` (new) — engine-aware model validator.
  `scripts/check_opencode_models.sh` kept as backward-compat alias.
- `scripts/agent_banner.sh` — shows engine + window assignment per
  pane.

The 11 markers from v10.0–v10.11 (refuse-ORCHESTRATOR routing,
clarification loop, auto-relaunch, [INBOX] auto-wake, memory layer,
resume detection, lean read list, Tech Stack Confirmation Protocol,
Prerequisite check, Phase gates, Stay-in-lane, Framework files
immutable) are all preserved.

### 2. 3-window tmux layout

Single-window 3×3 grid replaced with **3 windows** for better
ergonomics:

```text
Window 0 — OC       (1 pane)     ORCHESTRATOR — full size for chat
Window 1 — DESIGN   (2×2 panes)  PM, SA, BA, UX
Window 2 — DEV      (2×2 panes)  BE, FE, QA, DELIVERY
```

Switch windows with `Ctrl+B 0/1/2`. Routing scripts target panes by
pane ID (unique session-wide), so they work unchanged regardless of
window.

### 3. Prompt genericisation

`AGENTS.md` + 9 worker prompts had their few OpenCode-specific
mentions broadened to "the engine's built-in Task tool" etc. so
prompts work for either engine. No behavioural changes.

### Meta — preserving prior agreements

v10.0–v10.11 markers verified intact before AND after this change.
v10.12 is **purely additive**:

- Default engine = opencode → users on v10.11 get identical behaviour
  by re-running `start_agents_tmux.sh` without `--engine`.
- All existing prompts, scripts, memory files, phase gates,
  prerequisite checks, build-failure routing, and the framework-
  immutable rule continue to work.

## Changes from v10.10

### Framework files marked immutable + safe sync script

Two related additions answering a real concern: how do you upgrade
the framework on a running project without clobbering the team's
work, and how do you prevent an agent from quietly editing the
framework itself?

**1. `scripts/sync_framework_from_template.sh <TEMPLATE_PATH>`** —
copies ONLY the framework-owned files from a template directory
into the current project. Never touches `PRODUCT_IDEA.md`,
`TASK.md`, `memory/<ROLE>.md`, `memory/_PROJECT_STATE.md`, any
`docs/`/`planning/`/`reports/` deliverable, or `backend/`/
`frontend/` source. Every overwritten file is backed up to
`.framework_sync_backup/<timestamp>/` so you can roll back.

Supports `--dry-run` to preview changes:

```bash
bash scripts/sync_framework_from_template.sh ../product-engineering-template --dry-run
bash scripts/sync_framework_from_template.sh ../product-engineering-template
```

**2. AGENTS.md — "Framework files are immutable to agents"** — a
new universal rule listing every file no agent may write
(AGENTS.md, prompts/, scripts/, config/, .opencode/, etc.). Even
the Orchestrator and even when the user says "fix the prompt" —
the right response is `ask_orchestrator.sh` with a proposed diff,
and the user updates the template manually + re-syncs.

The only mutable, project-owned files explicitly carved out:
`TASK.md`, `memory/_PROJECT_STATE.md`, `memory/<ROLE>.md`.

### Meta — preserving prior agreements

v10.0–v10.10 untouched. v10.11 adds one script + one AGENTS.md
section. Nothing removed.

## Changes from v10.9

### Stay-in-your-lane + Build Failure Routing Protocol

v10.9 enforced phase gates and prereqs but said nothing about what
to do when DELIVERY hits a build failure caused by FE/BE source.
The user observed DELIVERY reading `frontend/nestfi/pages/*.py` and
preparing to fix `HStack.justify` errors itself — a clear role
boundary violation that defeats the multi-agent design.

v10.10 closes this with three additive pieces:

1. **`prompts/agents/DELIVERY.md` — "Build Failure Routing Protocol
   (HARD RULE)"**: when `docker compose build` fails, DELIVERY must
   capture the log, identify the failing service, route the right
   owner (BE / FE / SA-to-triage), notify Orchestrator, and exit.
   It explicitly forbids reading or editing any file under
   `backend/` or `frontend/` source. Includes a worked
   anti-pattern ("HStack.justify") so the model sees the exact
   shape to avoid.

2. **`prompts/agents/SA.md` — "Triage Protocol"**: SA is the natural
   triager when DELIVERY hands off an ambiguous failure. SA reads
   the log, picks the owner from `SOLUTION_ARCHITECTURE.md` and
   `API_CONTRACT.md`, routes BE / FE / itself (if the architecture
   itself is wrong), and notifies Orchestrator. SA does NOT fix the
   bug; it only decides ownership.

3. **`AGENTS.md` — "Stay in your lane" (universal)**: a table of
   per-role write boundaries plus the rule "when a task requires
   writing outside your boundary, do NOT do it yourself — route the
   right owner". All roles can freely read; only writes are
   restricted.

   ```text
   PM       docs/product/{PRD,ROADMAP}.md, planning/{BACKLOG,OPEN_QUESTIONS}.md
   SA       docs/architecture/*.md
   BA       docs/business/*.md
   UX       docs/product/{UX_FLOW,WIREFRAMES,DESIGN_NOTES}.md
   BE       backend/* (source), planning/BE_PLAN.md
   FE       frontend/* (source), planning/FE_PLAN.md
   QA       docs/qa/*.md, reports/*.md, plus test code if BE/FE didn't
   DELIVERY backend/Dockerfile, frontend/Dockerfile, docker-compose.yml,
            .env.example, docs/delivery/*.md
            (NOT backend/ source, NOT frontend/ source)
   ORCHESTRATOR TASK.md, memory/_PROJECT_STATE.md (coordinator only)
   ```

4. **`prompts/agents/ORCHESTRATOR.md` — "Build / test failure
   coordination"**: two shapes (DELIVERY routed BE/FE directly /
   DELIVERY routed SA to triage), and exactly what Orchestrator
   does for each (acknowledge to user, update active workstreams,
   wait for "done" notification, re-route DELIVERY).

### Meta — preserving prior agreements

Verified before AND after. v10.0–v10.9 rules untouched.

- v10.0  refuse ORCHESTRATOR; Task subagent disabled
- v10.1  no `--config`; AGENTS.md autoload
- v10.2  clarification loop; auto-relaunch
- v10.3  QA verdict gate; DELIVERY release pipeline; notify
- v10.4  auto-wake `[INBOX]`
- v10.5  durable `memory/`; resume detection
- v10.6  lean role-specific read list
- v10.7  Tech Stack Confirmation Protocol
- v10.8  Prerequisite check
- v10.9  Phase gates + quality gates

v10.10 is purely additive — new sections in DELIVERY.md, SA.md,
ORCHESTRATOR.md, AGENTS.md. No prior behaviour removed.

## Changes from v10.8

### Process discipline — phase gates with quality enforcement

v10.8's `check_prerequisites.sh` checked file inputs per role. v10.9
extends that into a **proper product-engineering phase gate** so the
Orchestrator can't skip ahead and DELIVERY can't ship a build with
unfixed critical bugs.

**New scripts:**

- `scripts/check_phase_gate.sh <PHASE>` and
  `scripts/check_phase_gate.sh --through <PHASE>` — verifies each
  phase's exit criteria, including semantic checks beyond file
  presence:

  - Phase 1 exit needs `TECH_STACK.md` to contain "Confirmed by user"
    (v10.7 protocol enforcement).
  - Phase 4 exit needs real source files in `backend/` AND `frontend/`.
  - Phase 5 exit needs `TEST_REPORT.md` starting with `VERDICT: PASS`
    AND `BUG_REPORT.md` clean of `OPEN_CRITICAL`/`OPEN_MAJOR`/
    `RETEST_FAIL`.
  - Phase 6 exit needs a live `http(s)://` URL in `RUNNING_APP.md`.

- `scripts/advance_phase.sh <NEW_PHASE>` — Orchestrator uses this to
  officially mark a phase done. Runs `check_phase_gate.sh --through
  <prev_phase>` first and **refuses** to advance if the gate fails
  (override only via `ADVANCE_PHASE_FORCE=1`). On success, updates
  `TASK.md` and `memory/_PROJECT_STATE.md` (current phase, checkbox,
  session log) and writes an entry to `memory/ORCHESTRATOR.md`.

**Extended `check_prerequisites.sh DELIVERY`:**

DELIVERY's pre-flight now hard-requires all of:

```text
reports/TEST_REPORT.md          (file present)
docs/architecture/TECH_STACK.md (file present)
_SIGNED_TECH_STACK_             ("Confirmed by user" line in TECH_STACK.md)
_VERDICT_PASS_                  (TEST_REPORT starts with VERDICT: PASS)
_NO_OPEN_CRITICAL_MAJOR_        (BUG_REPORT.md has no OPEN_CRITICAL /
                                 OPEN_MAJOR / RETEST_FAIL)
_CODE_BE_                       (backend/ has real source files)
_CODE_FE_                       (frontend/ has real source files)
```

If any fails, DELIVERY exits with a notification routing the right
upstream agent (QA to re-test, BE/FE to fix bugs, SA to re-run the
Tech Stack Confirmation Protocol).

**Bug-status convention** documented in `prompts/agents/QA.md`:

```text
OPEN_CRITICAL  OPEN_MAJOR  OPEN_MINOR
RETESTING      RETEST_PASS  RETEST_FAIL
FIXED          WONT_FIX
```

Release-blocking: `OPEN_CRITICAL`, `OPEN_MAJOR`, `RETEST_FAIL`.

**`delegate_phase.sh` warning**: each phase case now calls
`warn_if_prev_phase_incomplete` which runs `check_phase_gate.sh`
on the previous phase and prints a banner if it fails. Doesn't
refuse (might be a legit retry/patch), but the Orchestrator sees
the warning and can decide.

**AGENTS.md & ORCHESTRATOR.md** updated with "Process discipline"
and "Phase gate awareness" sections explaining when to use which
command (resume → `check_phase_gate --through`; before routing the
next phase → check the upstream gate; to mark a phase done →
`advance_phase.sh`).

### Meta — preserving prior agreements

Verified before AND after: v10.0–v10.8 rules untouched.

- v10.0  refuse ORCHESTRATOR; Task subagent disabled
- v10.1  no `--config`; AGENTS.md autoload
- v10.2  clarification loop; auto-relaunch
- v10.3  QA verdict gate; DELIVERY release pipeline; notify
- v10.4  auto-wake `[INBOX]`
- v10.5  durable `memory/`; resume detection
- v10.6  lean role-specific read list
- v10.7  Tech Stack Confirmation Protocol
- v10.8  Prerequisite check (fail fast on missing inputs)

v10.9 is purely additive — two new scripts, extended prereq for
DELIVERY, new prompt sections. No prior behaviour removed.

## Changes from v10.7

### Prerequisite check — fail fast on missing upstream inputs

Through v10.7, an agent that lacked its upstream inputs (e.g. BE
routed before SA had written `API_CONTRACT.md`) would silently
invent placeholder content rather than stopping. v10.8 closes that
hole with a hard dependency gate that every worker runs **before**
doing any other work.

**New script: `scripts/check_prerequisites.sh <ROLE>`**

- Defines per-role upstream inputs:

  ```text
  PM        → PRODUCT_IDEA.md
  BA        → PRODUCT_IDEA.md
  UX        → PRODUCT_IDEA.md, docs/product/PRD.md
  SA        → PRODUCT_IDEA, PRD, USER_STORIES, BUSINESS_REQUIREMENTS
  BE        → SOLUTION_ARCHITECTURE, TECH_STACK, API_CONTRACT,
              USER_STORIES
  FE        → UX_FLOW, API_CONTRACT, TECH_STACK
  QA        → USER_STORIES, API_CONTRACT, BACKLOG
  DELIVERY  → TEST_REPORT (must start with VERDICT: PASS),
              TECH_STACK
  ```

- Checks each file exists AND has substantive content
  (> 200 bytes by default; configurable via `PREREQ_THRESHOLD`).
- Special semantic check for DELIVERY: `reports/TEST_REPORT.md`
  must literally start with `VERDICT: PASS`, otherwise treated as
  blocked.
- For each missing file, names the **owner** (USER or an upstream
  agent role) so the caller knows whom to coordinate with.

- Exit codes: `0` if all prereqs satisfied, `1` if any missing /
  skeleton, `2` for usage errors.

**Wired into `route_to_pane.sh` task template (STEP 0)**

Every routed task now begins with:

```bash
bash scripts/check_prerequisites.sh <ROLE>
```

If it returns non-zero, the worker MUST file a notification
(`notify_orchestrator.sh` for agent-owned inputs, or
`ask_orchestrator.sh` for USER-owned inputs like `PRODUCT_IDEA.md`)
with the missing list and the upstream owners, append a "blocked"
line to `memory/<ROLE>.md`, and exit. **Do not** fake the missing
inputs.

**Worker prompts (all 8)**

Each `prompts/agents/<ROLE>.md` got a new
"Prerequisite check (DO NOT SKIP — fail fast on missing inputs)"
section inserted before the Memory protocol. Explicit rule: do not
write "TBD" placeholders, do not best-guess content for files
another role owns.

**Orchestrator prompt + AGENTS.md**

New "Missing-input handler" section in
`prompts/agents/ORCHESTRATOR.md` plus a universal rule in
`AGENTS.md`. When a worker notification arrives saying
"Cannot proceed — missing inputs: …. Need <upstream> to produce
them first":

1. Route each upstream owner to produce the missing artefact
   (parallel if independent).
2. Tell each upstream owner who is blocked downstream and ask them
   to `notify_orchestrator.sh "done"` when finished.
3. Update `memory/_PROJECT_STATE.md` Active workstreams.
4. When all upstreams report done, re-run `check_prerequisites.sh`
   on the blocked role; if it returns OK, re-route the blocked
   role with the same task.

### Meta — preserving prior agreements

Verified before AND after this change. v10.0–v10.7 rules untouched:

- v10.0  route_to_pane refuses ORCHESTRATOR; Task subagent disabled
- v10.1  `--config` flag dropped; AGENTS.md autoload
- v10.2  clarification loop; auto-relaunch loop
- v10.3  QA verdict gate; DELIVERY release pipeline; notify
- v10.4  auto-wake `[INBOX]` ping
- v10.5  durable `memory/` layer; resume detection; rescan_project
- v10.6  lean role-specific read list
- v10.7  Tech Stack Confirmation Protocol

v10.8 is purely additive — new STEP 0, new script, new prompt
section. No prior behaviour removed.

## Changes from v10.6

### Tech Stack Confirmation Protocol

Despite v10.3's "stop-and-ask" triggers, SA was still silently
picking the entire stack (Next.js / React / Tailwind / Postgres /
etc.) because the framework choices weren't in the trigger list and
the model treated them as "obvious defaults". v10.7 closes that hole
with a **mandatory protocol** SA (and to a lesser degree BE/FE) must
follow before committing to architecture artefacts.

**What's new:**

1. **SA.md** gets a new section "Tech Stack Confirmation Protocol
   (MANDATORY — read before any architecture work)". SA must:
   - Read context, draft a proposed stack with sensible defaults
     covering 12 dimensions (FE framework, FE language, UI system,
     BE language, BE framework, datastore, ORM, auth, cache/queue,
     hosting, code layout, package manager).
   - Call `ask_orchestrator.sh SA` with ONE batched question that
     lets the user say "yes" or override individual lines.
   - **STOP and exit** — do not write `TECH_STACK.md`, `ADR.md`,
     or `SOLUTION_ARCHITECTURE.md` until the user has answered.
   - After resume, write the architecture artefacts quoting the
     user's confirmed choices verbatim and including a "Confirmed
     by user (question id: SA_xxx)" line in `TECH_STACK.md`.

2. **SA stop-and-ask trigger list** expanded with the previously
   missing items: frontend/backend framework, language, ORM,
   auth approach, UI system, code layout, package manager.

3. **BE.md and FE.md** get a smaller "Tech Stack Confirmation
   Protocol — additive to SA's" section. They must honour what SA
   pinned, and only ask the user about second-order choices that
   SA left open (state mgmt, form lib, background job runner, etc.).
   They must NOT silently substitute "more modern" alternatives.

4. **AGENTS.md universal threshold** rewritten with concrete
   examples (Next.js vs Remix, FastAPI vs Django, Postgres vs Mongo)
   instead of the abstract "vendor / technology / cost tier"
   wording that the model glossed over.

5. **`delegate_phase.sh solution`** now contains an explicit
   step-by-step task message ordering SA to follow the protocol,
   with a clear "DO NOT write TECH_STACK.md before the answer
   arrives" instruction.

### Meta — preserving prior agreements

All v10.0–v10.6 rules were verified intact before this update and
are NOT touched by v10.7:

- v10.0  route_to_pane refuses ORCHESTRATOR; Task subagent disabled
- v10.1  `--config` flag dropped; AGENTS.md autoload
- v10.2  clarification loop; auto-relaunch loop
- v10.3  QA verdict gate; DELIVERY release pipeline; notification mechanism
- v10.4  auto-wake `[INBOX]` ping into Orchestrator TUI
- v10.5  durable `memory/` layer; session resume detection; rescan_project
- v10.6  lean role-specific read list

v10.7 is **purely additive** — new protocol sections inserted, no
prior behaviour removed.

## Changes from v10.5

### Lean role-specific read lists in every task file

Through v10.5 the task template (in `route_to_pane.sh`) told every
worker to read the same broad set of files — role prompt, AGENTS,
TASK, PRODUCT_IDEA, plus "the docs/ + planning/ files relevant to
this task". Models often defensively re-read 10+ files anyway,
including things irrelevant to their role (other roles' prompts,
governance docs, config docs, README, etc.). That's per-task token
waste of 5-15k tokens on a non-trivial project.

v10.6 makes `route_to_pane.sh` emit a **tailored read list per
target role**. The function `get_role_read_list <ROLE>` defines what
each role actually needs:

```text
PM       → PRODUCT_IDEA, PRD, ROADMAP, BACKLOG, OPEN_QUESTIONS,
            USER_STORIES
SA       → PRODUCT_IDEA, PRD, USER_STORIES, SOLUTION_ARCHITECTURE,
            TECH_STACK, ADR, API_CONTRACT
BA       → PRODUCT_IDEA, PRD, BUSINESS_REQUIREMENTS, USER_STORIES,
            DOMAIN_MODEL
UX       → PRODUCT_IDEA, PRD, UX_FLOW, WIREFRAMES, DESIGN_NOTES,
            USER_STORIES
BE       → API_CONTRACT, SOLUTION_ARCHITECTURE, TECH_STACK,
            USER_STORIES, BE_PLAN, BACKLOG
FE       → UX_FLOW, WIREFRAMES, DESIGN_NOTES, API_CONTRACT, FE_PLAN,
            BACKLOG
QA       → TEST_PLAN, TEST_CASES, USER_STORIES, API_CONTRACT,
            BACKLOG, TEST_REPORT, BUG_REPORT
DELIVERY → TECH_STACK, BE_PLAN, FE_PLAN, DELIVERY_PLAN,
            RUNNING_APP, RELEASE_NOTES, TEST_REPORT
```

`build_role_read_list_md` also annotates each entry with its current
state — "(does not exist yet)" / "(empty / skeleton)" — so the
worker knows whether to read or create.

### Explicit "DO NOT read by default" block

Each task file now lists the files workers should NOT re-read every
turn unless the task explicitly demands it:

```text
- prompts/agents/<OTHER_ROLES>.md
- planning/PANE_ROUTING_RULES.md
- planning/AGENT_WORKFLOW.md
- planning/ORCHESTRATOR_RUNTIME_RULES.md
- config/AGENT_MODELS.md
- config/OPENCODE_PERMISSION_POLICY.md
- VERSION.md, README.md
- .pane_logs/*, .pane_tasks/*
```

Combined with v10.5's `memory/<ROLE>.md` (which captures the
connective tissue without re-reading), this typically cuts per-task
read overhead by ~50%.

## Changes from v10.4

### Durable memory + session resume

This is the big continuity change. Previously every `opencode run`
worker started from a fresh context — re-reading the same docs,
re-deriving the same conventions, forgetting prior decisions. The
user had to keep retelling the team "we already decided X".

v10.5 introduces a **`memory/`** layer that lives alongside `docs/`
and `planning/`, and is **committed to git**:

```text
memory/
├── README.md                — discipline + format guide
├── _PROJECT_STATE.md        — team snapshot (Orchestrator owns)
├── ORCHESTRATOR.md          — Orchestrator's notes
├── PM.md   SA.md   BA.md    — per-role scratchpads
├── UX.md   BE.md   FE.md
├── QA.md   DELIVERY.md
```

Each role file is an append-only Markdown log of decisions /
conventions / gotchas. `_PROJECT_STATE.md` captures current phase,
active workstreams, pending questions, last deployed URL.

### What every agent must now do

`AGENTS.md` and every worker prompt was updated with a "Memory
protocol (DO NOT SKIP)" section. The discipline is:

1. **At start of every task** — read `memory/_PROJECT_STATE.md` and
   `memory/<ROLE>.md` BEFORE doing any work.
2. **At end of every task** — append a dated entry to
   `memory/<ROLE>.md`. Even if nothing notable happened, append a
   "routine task, no new entries" line so the slot isn't skipped.
3. **Orchestrator extra duty** — after every phase delegation,
   update `memory/_PROJECT_STATE.md` (current phase, completion
   checkboxes, active workstreams, session log).

`scripts/route_to_pane.sh` and `scripts/answer_role.sh` now embed
these instructions into every task file they generate, so workers
can't easily forget.

### Resume detection in `start_agents_tmux.sh`

When the script starts:

- It checks for `memory/<ROLE>.md` files larger than the skeleton
  (> 400 bytes) OR for substantive content in `docs/`.
- If found, prints `[v10.5] RESUME mode — <reason>` and writes
  `.agent_session_mode = RESUME`. Otherwise writes `FRESH`.
- The Orchestrator pane gets `AGENT_SESSION_MODE` env var, plus an
  automatic `[RESUME]` kickoff message a few seconds after OpenCode
  loads (via the same auto-wake mechanism we used in v10.4 for
  worker-fired inbox events).

The Orchestrator's prompt is updated so that when it sees `[RESUME]`
or a non-skeleton `_PROJECT_STATE.md`, its FIRST action is:

```bash
bash scripts/rescan_project.sh
```

…which prints a consolidated snapshot (state file + memory tails +
docs with content + source-code presence + Docker artefacts +
RUNNING_APP.md + inbox). The Orchestrator then summarises this for
the user in 3-5 bullets and waits for direction — it does NOT
auto-advance phases.

### New script

`scripts/rescan_project.sh` — "where did we leave off?" one-shot
report, used on resume and any time memory feels stale.

### Files modified

- `AGENTS.md` — Memory protocol section + Orchestrator's
  `_PROJECT_STATE.md` ownership + Session resume rule.
- `prompts/agents/ORCHESTRATOR.md` — Session resume vs fresh +
  Memory updates you own.
- `prompts/agents/{PM,SA,BA,UX,BE,FE,QA,DELIVERY}.md` — Memory
  protocol (read at start, append at end) injected before
  Clarification protocol.
- `scripts/route_to_pane.sh` — task file template now mandates
  memory read at step 1 and memory write at step 4.
- `scripts/answer_role.sh` — resume message references memory.
- `scripts/start_agents_tmux.sh` — RESUME detection, env var
  export, auto-kickoff for resume.
- `scripts/bootstrap_docs.sh` — also scaffolds `memory/` skeleton.
- `scripts/rescan_project.sh` — new.

## Changes from earlier versions (still in effect)

- **v10.4** — auto-wake Orchestrator via `[INBOX]` send-keys.
- **v10.3** — QA verdict gate, DELIVERY ships end-to-end,
  `notify_orchestrator.sh`, `release` phase shortcut, URL surface.
- **v10.2** — clarification loop (ask/answer/list), Orchestrator
  auto-relaunch, route_to_pane refuses ORCHESTRATOR.
- **v10.1** — dropped `--config` CLI flag, AGENTS.md auto-load.
- **v10.0** — real `.opencode/config.json`, correct subagent
  disable schema, verify_routing.

## Default model mapping (unchanged)

| Pane role | Full model ID |
|---|---|
| ORCHESTRATOR | `opencode-go/glm-5.1` |
| PM | `opencode-go/deepseek-v4-flash` |
| SA | `opencode-go/deepseek-v4-pro` |
| BA | `opencode-go/qwen3.6-plus` |
| UX | `opencode-go/mimo-v2.5` |
| BE | `opencode-go/deepseek-v4-pro` |
| FE | `opencode-go/kimi-k2.6` |
| QA | `opencode-go/qwen3.5-plus` |
| DELIVERY | `opencode-go/glm-5` |
