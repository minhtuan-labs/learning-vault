# Memory — BA

> Durable scratchpad for the **BA** pane. BA owns: business requirements, domain model, user stories.
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

### 2026-05-16 21:25 — Phase 0 Discovery Complete
Created three core business documents clarifying NestFi requirements:
- **BUSINESS_REQUIREMENTS.md**: Core rules for multi-tenancy, auth, transactions, accounts, reporting. Established that users can belong to multiple families, all transactions must be categorized, and cash withdrawals are expense transactions (not assets).
- **DOMAIN_MODEL.md**: Entity relationships (User, Family, FamilyMembership, Account, Category, Transaction) with constraints and invariants. Key insight: account balances are computed, not stored; transactions track direction (in/out).
- **USER_STORIES.md**: 28 stories across 7 groups (Auth, Family Mgmt, Accounts, Categories, Transactions, Reporting, Security). Included 5 open questions for user clarification (soft-delete vs hard-delete, edit history, session timeout, member removal, export format timing).

**Key conventions established**: Transaction amounts are always positive; direction field indicates in/out. Family-specific categories (not global). Email-based invitations with confirmation required. Multi-family support with session-based family selection.

**Decisions deferred to user** (open questions marked in USER_STORIES.md section 7).

**Blockers**: None — had PRODUCT_IDEA.md, which was sufficient input.

### 2026-05-16 21:37 — Account-Centric Design Confirmation
User clarified NestFi is account-centric (not person-centric, no bill-splitting). Updated three documents:
- **DOMAIN_MODEL.md**: Added "Design Principle: Account-Centric" section; clarified transactions belong to accounts, not people; no person-level tracking
- **USER_STORIES.md**: Added note before Story Group 5 to emphasize account selection in transaction stories, confirm no person-level tracking
- **OPEN_QUESTIONS.md**: Marked Q7 (Data Ownership & Privacy) as DECIDED → Full transparency (all members see all transactions, consistent with account-centric design)

**Key convention reinforced**: All family members have equal visibility to all accounts/transactions; created_by is metadata only, not person-level ownership. Cash withdrawal = single expense transaction from account (no sub-tracking).

### 2026-05-16 21:45 — Transaction & Member Management Rules Finalized
User answered three clarification questions; updated USER_STORIES.md and DOMAIN_MODEL.md:

**Q4 — Transaction Deletion (DECIDED):**
- All users can disable/enable (soft-delete/restore) transactions
- Disabled transactions excluded from P&L and dashboards but preserved for audit
- Only family owner can permanently delete (hard-delete) transactions; irreversible
- US-5.5 updated to reflect disable/restore with owner-only hard-delete

**Q5 — Edit History (DECIDED):**
- Yes, track full edit history with editor name, timestamp, and change summary
- Edit history immutable and visible to all family members
- US-5.4 updated; DOMAIN_MODEL.md added TransactionEditHistory entity

**Q7 — Member Removal (DECIDED):**
- Owner can disable (not hard-delete) family members
- Disabled members lose access but all transactions/edits remain intact
- Disabling is reversible; owner can re-enable members anytime
- US-2.4 new story added; DOMAIN_MODEL.md FamilyMembership updated with "disabled" status and disabled_at timestamp

**Files updated:**
- USER_STORIES.md: Added Transaction Lifecycle Rules note to Story Group 5; US-5.4 edit tracking + US-5.5 disable/restore; new US-2.4 member management; Open Questions section consolidated
- DOMAIN_MODEL.md: FamilyMembership added status "disabled" + disabled_at; Transaction added enabled flag + updated_at; new TransactionEditHistory entity; Dashboard/Reporting clarified (enabled only); Data Constraints & Invariants updated

**Phase 0 Discovery now complete** — all three open questions resolved, user stories and domain model finalized, ready for Phase 1 (Solution Design).
User clarified NestFi is account-centric (not person-centric, no bill-splitting). Updated three documents:
- **DOMAIN_MODEL.md**: Added "Design Principle: Account-Centric" section; clarified transactions belong to accounts, not people; no person-level spending tracking
- **USER_STORIES.md**: Added note before Story Group 5 to emphasize account selection in transaction stories, confirm no person-level tracking
- **OPEN_QUESTIONS.md**: Marked Q7 (Data Ownership & Privacy) as DECIDED → Full transparency (all members see all transactions, consistent with account-centric design)

**Key convention reinforced**: All family members have equal visibility to all accounts/transactions; created_by is metadata only, not person-level ownership. Cash withdrawal = single expense transaction from account (no sub-tracking).

### 2026-05-16 21:58 — Phase 2 Backlog & Spec Refinement
Transitioned to Phase 2 (BACKLOG_AND_SPEC). Reviewed PRD, BUSINESS_REQUIREMENTS, UX_FLOW, and 28 user stories.
- **Planning/BACKLOG.md created**: Organized 28 stories into 7 groups with P0/P1/P2 prioritization, dependencies, and recommended implementation sequencing (4 phases: Auth, Finance, Dashboard, Polish). Clear MVP gate criteria.
- **USER_STORIES.md reviewed**: All 28 stories have complete acceptance criteria; open questions section consolidated and marked DECIDED/DEFERRED; no new requirements discovered from UX_FLOW
- **Phase 2 coherence verified**: Stories align with PRD scope (MVP: auth, family mgmt, transactions, dashboard, exports); UX flows map to all major user journeys; BUSINESS_REQUIREMENTS constraints enforced (multi-tenancy, categorization, account-centric model)
- **Key convention**: Session timeout deferred (PRD specifies manual logout only); export reports marked stretch goal (may move to v1.1); all default categories pre-seeded on family creation

**No scope gaps detected**. Phase 2 outputs ready for downstream (SA for API contract, FE/BE for planning phase).
