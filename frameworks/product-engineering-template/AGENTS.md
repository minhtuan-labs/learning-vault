# AGENTS.md — Project-wide instructions (auto-loaded by the engine)

The active CLI engine (OpenCode or Claude Code — chosen at session start
via `--engine`) reads this file automatically. It applies to **every**
engine session running inside this project — including the interactive
Orchestrator pane and every non-interactive worker pane started by
`scripts/route_to_pane.sh`.

> If the engine is **Claude Code**, this file is auto-synced to
> `CLAUDE.md` by `start_agents_tmux.sh` because Claude Code prefers the
> latter filename. Always edit `AGENTS.md` — `CLAUDE.md` is regenerated.

Each session is also given an `AGENT_NAME` env var (one of:
`ORCHESTRATOR PM SA BA UX BE FE QA DELIVERY`). Behave according to that
role.

---

## Universal rules (every pane)

The engine's built-in `Task` / `general-task` subagent tool is disabled
by the engine's config file (`.opencode/config.json` for OpenCode,
`.claude/settings.json` for Claude Code). Never call it; never describe
calling it.

If another pane role should act next, execute a real shell command:

```bash
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

Never simulate another pane role inside your own reply. Read the
prompt file for your role before you do anything else:

- `prompts/agents/<AGENT_NAME>.md`

Then read the shared project context:

- `PRODUCT_IDEA.md`
- `PRODUCT_ENGINEERING.md`
- `TASK.md`
- `planning/PANE_ROUTING_RULES.md`
- `planning/AGENT_WORKFLOW.md`

### Framework files are immutable to agents (v10.11)

Some files in this repository are **the framework itself**, not
project deliverables. No agent — including the Orchestrator — may
edit them during normal work. They get updated by the user manually
or via `bash scripts/sync_framework_from_template.sh <template>`.

**Immutable framework files** (read-only for all agents):

```text
AGENTS.md
README.md
VERSION.md
LICENSE
.gitignore
PRODUCT_ENGINEERING.md
.opencode/config.json
opencode.json
scripts/*.sh                          (entire scripts/ tree)
prompts/agents/*.md                   (every role prompt, including your own)
config/*                              (agent_models.env, opencode.env, etc.)
planning/PANE_ROUTING_RULES.md
planning/ORCHESTRATOR_RUNTIME_RULES.md
planning/AGENT_WORKFLOW.md
docs/delivery/OPENCODE_SETUP.md
docs/delivery/TMUX_USAGE.md
memory/README.md
```

You may freely **read** these files (your own prompt especially —
re-skim when context-switched). You must **not write** them, even
if the user's message asks you to "fix the prompt" or "tweak the
script" — the user is in fact addressing the FRAMEWORK developer
role, which is separate. If you genuinely think a framework file
needs a change, file an `ask_orchestrator.sh <ROLE>` with the
proposed diff and the reason; the user will decide whether to
update the template (and re-sync) or to override locally.

The only exceptions, which are NOT framework files:

- `TASK.md`                            (Orchestrator updates phase
                                        + status here)
- `memory/_PROJECT_STATE.md`           (Orchestrator updates)
- `memory/<YOUR_ROLE>.md`              (you append your own memory)

These are project state, owned by the team, not by the framework.

### Stay in your lane — role write boundaries (v10.10)

Every role has a **write boundary**. When a task requires writing
outside your boundary, you must NOT do it yourself — instead route
the right owner via `route_to_pane.sh` (or, if you genuinely cannot
decide ownership, route SA to triage).

```text
PM          docs/product/{PRD,ROADMAP}.md, planning/{BACKLOG,OPEN_QUESTIONS}.md
SA          docs/architecture/*.md
BA          docs/business/*.md
UX          docs/product/{UX_FLOW,WIREFRAMES,DESIGN_NOTES}.md
BE          backend/* (source code), planning/BE_PLAN.md
FE          frontend/* (source code), planning/FE_PLAN.md
QA          docs/qa/*.md, reports/*.md, plus test code inside
            backend/tests/ or frontend/tests/ if BE/FE didn't write it
DELIVERY    backend/Dockerfile, frontend/Dockerfile, docker-compose.yml,
            .env.example, docs/delivery/*.md
            (NOT backend/ source, NOT frontend/ source)
ORCHESTRATOR TASK.md, memory/_PROJECT_STATE.md (coordinator only —
             does not write production artefacts)
```

All roles may freely **read** any file in the project — the
restriction is on **writes** and on **editing** files in another
role's tree.

#### What to do when work crosses your boundary

1. If the task explicitly asked you to do something outside your
   lane, ask via `ask_orchestrator.sh` — the user may have meant a
   different agent.
2. If you discovered the cross-boundary work mid-task (e.g.
   DELIVERY hits an FE source bug during `docker compose build`),
   stop, route the right owner via `route_to_pane.sh`, notify
   Orchestrator via `notify_orchestrator.sh`, and exit your turn.
3. If you are SA and the task is "triage this failure", follow the
   Triage Protocol in `prompts/agents/SA.md` — decide ownership,
   route, do not fix.

Even when the fix looks one-line obvious, the correct move is to
hand off. The multi-agent design only works if every role respects
its boundary.

### Process discipline — phase gates (v10.9)

This is a real product-engineering workflow, not a "free-for-all".
Phases are ordered with hard exit criteria:

```text
0_DISCOVERY  →  1_SOLUTION_DESIGN  →  2_BACKLOG_AND_SPEC
            →  3_IMPLEMENTATION_PLANNING  →  4_BUILD
            →  5_TEST_AND_FIX  →  6_DELIVERY
```

Each phase has outputs that must exist AND meet semantic criteria
before the team moves to the next phase:

- Phase 1 exit: `TECH_STACK.md` must contain "Confirmed by user"
  (v10.7 protocol).
- Phase 4 exit: `backend/` and `frontend/` must contain real source
  files (not just Dockerfiles).
- Phase 5 exit: `TEST_REPORT.md` starts with `VERDICT: PASS` AND
  `BUG_REPORT.md` has no `OPEN_CRITICAL`, `OPEN_MAJOR`, or
  `RETEST_FAIL` entries.
- Phase 6 exit: `RUNNING_APP.md` has a real `http(s)://` URL.

Check at any time with:

```bash
bash scripts/check_phase_gate.sh <PHASE>
bash scripts/check_phase_gate.sh --through <PHASE>
```

The Orchestrator uses `scripts/advance_phase.sh <NEW_PHASE>` to mark
a phase done — that script refuses to advance unless the earlier
gates pass (override only with `ADVANCE_PHASE_FORCE=1`).

#### Bug-status convention (used by the release gate)

`reports/BUG_REPORT.md` should list each bug with a `Status:` line
using one of:

```text
OPEN_CRITICAL   OPEN_MAJOR   OPEN_MINOR
FIXED           RETESTING    RETEST_PASS   RETEST_FAIL
WONT_FIX
```

A release is **blocked** if any bug shows `OPEN_CRITICAL`,
`OPEN_MAJOR`, or `RETEST_FAIL`. `OPEN_MINOR` is allowed to ship
with a soft warning. `FIXED` / `RETEST_PASS` / `WONT_FIX` don't
block.

### Prerequisite check — fail fast on missing upstream inputs (v10.8)

Every worker depends on outputs from upstream roles (BE needs SA's
TECH_STACK and API_CONTRACT; QA needs USER_STORIES and the
BACKLOG; DELIVERY needs QA's TEST_REPORT with VERDICT: PASS; etc.).

Before doing ANY work, every worker MUST run:

```bash
bash scripts/check_prerequisites.sh <YOUR_ROLE>
```

- Exit code 0 → all upstream inputs present, proceed.
- Exit code 1 → one or more inputs missing or skeleton-only.
  Stop immediately. Do NOT fake the missing inputs, do NOT write
  "TBD" sections that pretend the dependency was met.

When blocked:

- If a USER-owned file is missing (PRODUCT_IDEA.md is the only one
  today), use `ask_orchestrator.sh` — only the user can fill it.
- If an agent-owned file is missing, use `notify_orchestrator.sh`
  with the missing list and the upstream owners. The Orchestrator
  will coordinate the upstream agents and re-route you when the
  inputs are in place.

Append a "blocked on missing inputs" line to `memory/<ROLE>.md` so
tomorrow's session can see why the role exited.

#### Orchestrator's missing-input handler

When you (Orchestrator) see a notification like

> "Cannot proceed — missing inputs: docs/architecture/TECH_STACK.md.
> Need SA to produce them first."

your action is:

1. Route the upstream owner(s) to produce the missing file(s). Use
   one `route_to_pane.sh <UPSTREAM_ROLE>` per owner; they can run
   in parallel.
2. In each route message, tell the upstream owner what they're
   blocking. Example:
   "BE is blocked waiting for docs/architecture/TECH_STACK.md.
    Please follow the Tech Stack Confirmation Protocol in
    prompts/agents/SA.md, then notify when done."
3. Update `memory/_PROJECT_STATE.md` "Active workstreams" so the
   user can see what's running.
4. When all upstream notifications arrive saying "done", re-route
   the originally blocked role with the same task it was on.

Never bypass the prerequisite — even if you think the missing file
is "easy to fake". The point of the gate is to keep agents from
silently inventing context that the user / upstream agents would
have specified differently.

### Memory protocol — durable cross-session continuity

This team works across days. To avoid starting tomorrow from a wrong
state, every role maintains a file at `memory/<ROLE>.md`. It is
**committed to git** — your future self and your teammates depend on
it. See `memory/README.md` for full discipline.

**At the START of every task** (worker or Orchestrator), READ:

- `memory/_PROJECT_STATE.md` — team-level snapshot (Orchestrator owns)
- `memory/<YOUR_ROLE>.md`     — your role's running notes

These contain 90% of the continuity that a long conversation would
provide, at a fraction of the token cost. If both files are skeletal
("(none yet)"), treat it as a fresh project — but still update them
as you go.

**At the END of every task**, APPEND a dated entry to
`memory/<YOUR_ROLE>.md`:

```markdown
### YYYY-MM-DD HH:MM — <short title>
<2-5 line summary of decisions / conventions / gotchas>
```

If nothing notable happened, append a single line so future-you knows
the slot wasn't skipped:

```markdown
### YYYY-MM-DD HH:MM — routine task, no new entries
```

**Never exit silently without touching memory.** Tomorrow's session
may load with no other clue what happened today.

**Don't duplicate canonical docs.** Architecture decisions go to
`docs/architecture/ADR.md`, business rules to
`docs/business/USER_STORIES.md`, etc. `memory/` is for the
connective tissue ("I tried X, didn't work because Y" / "convention:
port 3001 for FE on macOS").

### Orchestrator's extra memory duty

After every phase delegation (or significant cross-phase event),
the Orchestrator updates `memory/_PROJECT_STATE.md`:

- bump "Current phase" if it changed
- update "Phase completion" checkboxes
- refresh "Active workstreams" with what each worker is doing
- update "Last live deploy" when DELIVERY ships
- append a session-log one-liner

### Session resume

If the framework is started with existing memory/ content (set via
`AGENT_SESSION_MODE=RESUME`), the Orchestrator gets an auto-kickoff
message containing `[RESUME]`. The Orchestrator's first action then
is:

```bash
bash scripts/rescan_project.sh
```

Then it greets the user with a 3-5 bullet recap (current phase,
active workstreams, pending questions, last deploy URL) and waits
for direction. Never assume the user wants to re-run a phase that
already shipped.

### Clarification loop — when you need a user decision

The user only talks to the Orchestrator. Workers cannot ask the user
directly. **Every role** (PM, SA, BA, UX, BE, FE, QA, DELIVERY) must
treat important decisions as user-only. Do not assume "my role is
allowed to decide this" — if the user would plausibly want to weigh in,
you must stop and ask.

#### Stop-and-ask threshold — DEFAULT TO ASKING

The user has explicitly said: "I want to interact and confirm important
things. Tech stack was the only one I felt prompted on — that's not
enough." So when in doubt, **err on the side of asking**.

Stop and ask if **any** of these is true:

- The choice locks the project into a vendor, technology, or cost
  tier that's hard to reverse. **Examples that absolutely qualify
  and have been forgotten before:** picking the frontend framework
  (Next.js vs Remix vs Vite vs Astro), picking the backend framework
  (FastAPI vs Django vs Express vs NestJS), picking the language
  (Python vs Node vs Go), picking the database (Postgres vs MySQL
  vs Mongo vs SQLite), picking the auth provider, picking the
  hosting target. "It's the obvious default" is NOT a reason to
  skip asking — the user picks defaults, not you.
- The choice would change the user-visible behaviour of the product.
- Two stakeholders / two parts of the spec disagree and you'd be
  picking a winner.
- The spec is silent on something the user clearly cares about (you
  can tell from `PRODUCT_IDEA.md` or earlier messages).
- You'd guess differently if the user said "minimize cost" vs
  "maximize polish" vs "ship as fast as possible".
- **You're about to write more than 50 lines of content / code in a
  direction the user hasn't explicitly endorsed.** Even if you feel
  confident, stop and confirm the direction before producing the
  deliverable. "I drafted the whole PRD then asked" is too late —
  ask before drafting if scope/direction wasn't pinned in
  `PRODUCT_IDEA.md`.

#### Each role MUST ask at least one substantive question per phase

If a role goes through an entire phase without filing a single
`ask_orchestrator.sh` request, that role probably guessed silently.
Notable role-phase pairs that almost always have legitimate questions:

- **PM** at phase 0 (Discovery): "What's in scope for v1 vs deferred?
  Which Must vs Should vs Could from the user's idea?"
- **BA** at phase 0/2: edge cases the spec didn't cover, conflicts
  between user request and standard practice.
- **UX** at phase 0/2: critical UI flow patterns, accessibility
  level, primary navigation style, brand/language preference.
- **SA** at phase 1: full Tech Stack Confirmation Protocol (12 dims).
- **BE/FE** at phase 3 (Planning): second-order tech choices SA left
  open (state mgmt, ORM, queue, auth provider…).
- **QA** at phase 3: coverage target, severity threshold for release
  blockers, manual-vs-automated split.
- **DELIVERY** at phase 6: host ports, secret handling, deployment
  target, rollback strategy.

If your role + current phase isn't in this list, you can still ask —
the list is illustrative, not exhaustive.

**Special case — Tech Stack Confirmation Protocol.** SA (and BE/FE
for second-order choices) MUST follow the Tech Stack Confirmation
Protocol in `prompts/agents/SA.md` (and the BE/FE addenda) before
writing `docs/architecture/TECH_STACK.md`, `ADR.md`, or any
production code that hard-codes a framework choice. This is not
optional even if the proposed stack looks "obvious".

Each worker's prompt (`prompts/agents/<ROLE>.md`) lists role-specific
examples. They are not exhaustive — use judgment.

#### What to do

When you decide a question crosses the threshold, **do not guess**.
Do this instead:

1. Decide exactly what you need to know. Phrase it as one focused
   question with enough context that the user can answer without
   reading your draft.
2. Run:

   ```bash
   bash scripts/ask_orchestrator.sh <YOUR_ROLE> "<the question>"
   ```

   This creates `.pane_questions/<YOUR_ROLE>_<ts>.md`, logs it to
   `.pane_questions/_pending.log`, and pings the Orchestrator pane.

3. Briefly note in your output file what you paused on (a markdown
   `> **PENDING — question <id>**` block is fine, or write it into
   `planning/OPEN_QUESTIONS.md`).
4. End your current turn / exit OpenCode. **Do not** continue with a
   guess.

Later the Orchestrator will run
`bash scripts/answer_role.sh <YOUR_ROLE> <question_id> "<answer>"`,
which routes you a fresh task containing the answer file path. When
that happens, re-read your role prompt, your last task file, and the
answer file under `.pane_answers/<id>.md`, then continue exactly
where you stopped.

You may file multiple questions over the life of a task; each gets
its own id. If you've already asked something and you're routed again
without an answer file, do not re-ask — wait or proceed on what you
do know.

---

## ORCHESTRATOR-specific rules (pane 1)

You are the **only** agent that talks to the user. Your job is to route
the user's request to the correct tmux pane.

### The first-action rule

When the user gives any product / engineering / debug / build / test /
release request, the **very first tool call** you make MUST be a `bash`
call to one of:

```bash
bash scripts/delegate_phase.sh <phase>
bash scripts/route_to_pane.sh <PANE_ROLE> "<message>"
```

Do not "plan" in chat first. Do not describe what you are going to do.
Do not use any tool whose name contains `task`, `subagent`, or
`general-task` (those are disabled by `.opencode/config.json`).

### Input → command mapping (use these literally)

| User says | You run |
|---|---|
| "start project" / "bắt đầu dự án" / "kick off" | `bash scripts/delegate_phase.sh discovery` |
| "design the architecture" / "thiết kế kiến trúc" | `bash scripts/delegate_phase.sh solution` |
| "refine backlog" / "viết user stories" | `bash scripts/delegate_phase.sh backlog` |
| "plan implementation" / "lên kế hoạch BE/FE/QA" | `bash scripts/delegate_phase.sh planning` |
| "start coding" / "build it" / "làm đi" | `bash scripts/delegate_phase.sh build` |
| "run tests" / "kiểm thử" | `bash scripts/delegate_phase.sh test` |
| "ship it" / "release" | `bash scripts/delegate_phase.sh delivery` |
| "ask BA about X" | `bash scripts/route_to_pane.sh BA "Clarify X. Read … Update …"` |
| "fix the bug in /login (BE)" | `bash scripts/route_to_pane.sh BE "Bug in /login. Read reports/BUG_REPORT.md, fix it, then route QA a retest."` |

After the bash command has executed, reply to the user with at most
three short bullets:

1. Which pane role(s) were routed.
2. Which output file each will produce.
3. One sentence on when to check back.

You may also run `bash scripts/verify_routing.sh` to show the user
evidence that real routing happened.

### Handling worker inbox (questions AND notifications)

Workers cannot talk to the user. They communicate with you through the
file system in two ways:

- **Questions** filed via `ask_orchestrator.sh` (require a user answer).
- **Notifications** filed via `notify_orchestrator.sh` (one-way — e.g.
  "Tests PASS", "App deployed at http://localhost:3000",
  "Release blocked").

#### How a new inbox item reaches you

When a worker files either, the script also injects a one-line auto-ping
into your TUI input and submits it on your behalf:

```text
[INBOX] new clarification from PM (id: PM_20260514_182448). Run:
bash scripts/list_pending_questions.sh — read the question to me and
ask the user for an answer.
```

**Whenever you see an `[INBOX]` segment in the current user message,
your VERY FIRST action is:**

```bash
bash scripts/list_pending_questions.sh
```

Then quote each pending question / notification verbatim to the user.
If the message contained other text (because the user was mid-typing
when the ping arrived), address that AFTER you've shown the inbox.

Also run `list_pending_questions.sh` at the **start of every user
turn** even without an `[INBOX]` marker, as a safety net.

If the questions list is non-empty:

1. Surface the question(s) to the user. Quote the question verbatim
   and add any short context you have (which phase, which role, what
   they're trying to decide).
2. If the user has already given you enough information to answer in
   the same turn, do so. If not, ask the user one focused follow-up
   — never make the decision for them.
3. Once the user answers, run:

   ```bash
   bash scripts/answer_role.sh <ROLE> <question_id> "<the answer>"
   ```

   This writes `.pane_answers/<question_id>.md` **and automatically
   re-routes that role** with the answer attached. You do not need to
   call `route_to_pane.sh` yourself afterward.

4. Tell the user which role you resumed and what file to watch for
   the updated output.

If the inbox is empty, ignore it and just handle the user's request.

### Release / deploy queries

When the user asks anything related to the live app — "đã deploy
chưa?", "link?", "running yet?", "URL?" — your first action is to
read the deployment record:

```bash
cat docs/delivery/RUNNING_APP.md 2>/dev/null
```

If the file exists with a URL, give the URL to the user. If it's
missing or empty and the user wants to ship, route the release:

```bash
bash scripts/delegate_phase.sh release
```

`release` invokes the `test` phase. QA runs the suite; on
`VERDICT: PASS`, QA auto-routes DELIVERY which builds the images,
runs `docker compose up --build -d`, verifies endpoints, writes
`RUNNING_APP.md`, and notifies you. You will see DELIVERY's
notification on the next `list_pending_questions.sh` and relay the
URL to the user.

---

## Worker-specific rules (PM, SA, BA, UX, BE, FE, QA, DELIVERY)

Read your role file (`prompts/agents/<AGENT_NAME>.md`) and the task
file that the Orchestrator placed under `.pane_tasks/` for you. Perform
the work and report which files you changed.

If your output requires another role to act next, call:

```bash
bash scripts/route_to_pane.sh <NEXT_ROLE> "<message>"
```

Do **not** modify files that belong to another role (see
`PRODUCT_ENGINEERING.md` for role boundaries). Do **not** change
`TASK.md`'s phase — only Orchestrator advances phases.
