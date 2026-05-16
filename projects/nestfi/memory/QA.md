# Memory — QA

> Durable scratchpad for the **QA** pane. QA owns: test plan, test execution, test report, release gate.
>
> READ this file at the start of every task (alongside
> `memory/_PROJECT_STATE.md`). APPEND a dated entry before exiting any
> OpenCode turn. See `memory/README.md` for format and discipline.

## Decisions

(none yet)

## Conventions

(none yet)

## Gotchas

(none yet)

## Open items I'm tracking

- Manual testing checklist to be created in Phase 5 (email validation, UI flows, multi-browser)
- TEST_CASES.md to be written during Phase 5 (49+ test cases mapped to user stories)

---

### 2026-05-16 17:39 — TEST_PLAN.md Created

**Completed:** Comprehensive TEST_PLAN.md for Phase 3 (Implementation Planning)

**Key Decisions:**
- Test pyramid: Unit (60%, ~110 tests), Integration (35%, ~78 tests), E2E (5%)
- Coverage targets: 70% unit, 100% integration (21/21 endpoints), 100% manual
- Severity convention: CRITICAL/MAJOR block release; MINOR soft warning
- Timeline: Phase 5 = 3 days (Day 1: test + manual 10h, Day 2: fix 8h, Day 3: validate 4h)
- Manual vs Automated split: 70% automated (CRUD, auth, validation), 30% manual (UI, email, browsers, performance)

**Convention Established:**
- Bug report uses status: OPEN_CRITICAL, OPEN_MAJOR, OPEN_MINOR, RETESTING, RETEST_PASS, RETEST_FAIL, FIXED, WONT_FIX
- TEST_REPORT.md must start with VERDICT: PASS or FAIL
- Release blocked if any OPEN_CRITICAL, OPEN_MAJOR, or RETEST_FAIL exists
- Phase 5 exit gate: 11 checkboxes that all must be true for PASS

**Gotchas:**
- Email delivery SLA not testable in unit/integration tests (mock SMTP); must validate manually in Phase 5
- Soft-delete filter leak is critical risk: query tests must verify `deleted_at IS NULL` on EVERY transaction SELECT
- Permission bypass is critical risk: need comprehensive RBAC test matrix (all roles × all endpoints)
- Timezone/daylight savings bugs possible: use freezegun to mock time in unit tests

**Next Steps (Phase 5):**
- Create TEST_CASES.md with 49+ test cases mapped to user stories
- Create TEST_REPORT.md with VERDICT: PASS/FAIL and detailed metrics
- Create BUG_REPORT.md with all issues found, status, assignments
- Ensure coverage.html (pytest-cov report) shows ≥70%
