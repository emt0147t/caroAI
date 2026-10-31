# CaroAI Phase 4 — M5 Handover and Release Evidence Checklist

> **Status:** Working handover; not release approval.
> **Prepared:** 2026-10-29
> **Owner:** M5 — Database, QA, Documentation
> **Working branch:** `feature/m5-sprint4-qa`
> **QA matrix:** [Phase 4 M5 QA Matrix](phase4-m5-qa-matrix.md)
> **Release decision:** **BLOCKED / NO-GO**

## 1. Purpose and scope

This document converts the Phase 4 QA matrix into an actionable handover for M1–M4. It records evidence requirements and ownership; it does not claim that work owned by another member has been executed. Historical CI, PR-only browser tests, Docker builds, and disposable Compose tests must not be presented as public production evidence.

## 2. Verified evidence snapshot

The evidence below belongs only to the recorded workflow snapshots. Re-run affected gates if the candidate SHA changes.

| Evidence | Recorded result | What it does not prove |
|---|---|---|
| [CI #299 — general Python tests/lint](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165472) | 218 passed, 11 skipped, 1 warning | Skipped tests are not passes; this is not production validation |
| [CI #299 — PostgreSQL acceptance](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481) | 15 passed, 0 skipped; zero-skip guard passed | Real AI engine integration is not established by tests that monkeypatch the AI call |
| [CI #299 — Compose persistence](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165000) | Passed in disposable Compose stack; API restart/read-back covered | Does not establish production persistence after redeploy |
| [CI #299 — Docker build](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555667124) | Image build passed | Image was not thereby published or deployed |
| [Browser E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162) | 13/13 Playwright tests passed on PR #38 merge-validation snapshot `a656439`; PR head `02b2ca64fba7ad8ec1387ca25738917bc6bc2ddc` | PR-only validation; not the final candidate or public production smoke |

Baseline for CI #299: `138164803f3537d15ca90d9bc358f3f86528c4f3`. See the [full matrix](phase4-m5-qa-matrix.md) for the test-layer breakdown and T-01–T-17 statuses.

### Current C1 validation snapshot (2026-10-29)

- [CaroAI CI #321](https://github.com/emt0147t/caroAI/actions/runs/40892411531) completed successfully. Logs explicitly show checkout of PR #39 merge-validation SHA `34cf32d8c97377d37c2b468785e2a01c03f469bf`, formed by merging PR head `bf0f8e06c668eb30c9e939ad87ac12ed049c2626` into `develop` base `138164803f3537d15ca90d9bc358f3f86528c4f3`. Python tests/lint: **218 passed, 11 skipped, 1 warning**; dedicated PostgreSQL acceptance: **15 passed, 0 skipped**, zero-skip guard passed; Compose persistence, frontend regression and Docker build succeeded. Production publish/deploy was skipped.
- [Browser E2E #55](https://github.com/emt0147t/caroAI/actions/runs/40892411540) completed successfully: **13/13 Playwright tests passed** on the same merge-validation SHA `34cf32d8c97377d37c2b468785e2a01c03f469bf`, including History retry/reload, PvP, PvAI, duplicate-submit prevention, HTTP error handling, network recovery, AI retry, terminal lock, draw and responsive viewports.
- The earlier [CI #307](https://github.com/emt0147t/caroAI/actions/runs/40874711154) and [E2E #50](https://github.com/emt0147t/caroAI/actions/runs/40874711121) logs reported checkout commit `21505ad2541d5be6135ed84fc33697146cf75b8e`; do not use those runs as exact-SHA proof. The fresh #321/#55 logs resolve the PR validation provenance.
- **C1 is closed for PR #39 documentation/QA-matrix validation only.** It does not prove a new application-code regression, close C2 database guard, satisfy benchmark acceptance, or authorize production release. Release remains **BLOCKED / NO-GO**.
- PR #35 remains a separate draft targeting `main`; its in-memory `GET /api/history` implementation is not evidence of persisted History. The API owner/M1 must record the contract decision before any merge decision.


## 3. Required handover actions

| Priority | Owner | Action | Evidence required before sign-off |
|---|---|---|---|
| P0 | M1, with M5 recording | Review PR #35 against the persisted History contract and actual target branch | Written decision linked to the diff and contract; verify base/head and avoid merging the in-memory History implementation as if it were DB-backed |
| P0 | M2, supported by M4; M5 audits | Run tactical AI regression and benchmark on the exact candidate; include Linux/Docker measurements | Full source SHA, environment/CPU/container, command, fixture/trial method, tactical outcomes, raw CSV/JSON, report, and team decision on whether p95 ≤ 2,000 ms is a target or SLO |
| P0 | M4 + independent M1 reviewer | Confirm production Environment protections and perform approved release promotion from the approved branch/SHA | Required reviewer, prevent-self-review, branch restrictions, successful release workflow, immutable full-SHA image, deployment ID/status |
| P0 | M3/M4 execute; M5 records | Run public HTTPS health/readiness and PvP/PvAI/History smoke after deployment | Public URL/environment, exact source/image SHA, browser/version, results and artifact links |
| P0 | M4 executes; M5 verifies; M1 signs off | Verify a designated test game's moves/history after production redeploy | Before/after game ID and state evidence, deployed image SHA, successful read-back; do not use destructive tests on shared/production data |
| P1 | M1–M5 | Review issue closure recommendations individually | Each issue mapped to its own acceptance criteria and evidence; no blanket closure |
| P1 | M5 + M1–M4 | Prepare a concise demo and failure-triage record | Demo follows the checklist below and explicitly calls out unsupported/unverified claims |

## 4. Seven-minute demo checklist

Use only after the team has a working environment. If public deployment is unavailable, label the demonstration as local/CI and do not describe it as production.

1. **0:00–0:45 — Identify the build:** state environment, source SHA, image SHA if deployed, and which workflow validated that snapshot.
2. **0:45–2:00 — Create and read a game:** create a game, record its ID, retrieve it through the API, and show the authoritative board/mode/status.
3. **2:00–3:15 — Play PvP:** alternate X/O moves; demonstrate turn enforcement and rejection of an invalid/occupied move.
4. **3:15–4:30 — Play PvAI:** request an AI move through the backend and show the returned/persisted state. State whether the live AI engine or a deterministic test double is in use.
5. **4:30–5:15 — History and reload:** show History, refresh/reopen, and compare game/move state. Distinguish DB-backed evidence from in-memory behavior.
6. **5:15–6:15 — Persistence evidence:** if approved, show a designated test game before and after the relevant restart/redeploy; otherwise show the Compose test artifact and explicitly state that production redeploy persistence is unverified.
7. **6:15–7:00 — QA and risks:** show the matrix, benchmark status, open PR #35 decision, live smoke status, and current GO/NO-GO decision.

Do not manufacture screenshots, game IDs, benchmark numbers, public URLs, or successful deployment results. If a step fails, record the failure and preserve logs rather than repeating until a misleading success is obtained.

## 5. Release evidence capture template

Copy this template into the release record only after collecting actual values:

- Candidate source SHA:
- Approved branch / PR:
- CI workflow URL and exact SHA:
- General test result (passed / failed / skipped / warnings):
- Dedicated PostgreSQL acceptance (passed / failed / skipped):
- Compose persistence after API restart:
- Browser E2E workflow, tested SHA, and result:
- AI tactical regression workflow and result:
- AI benchmark report + raw CSV/JSON:
- CPU / OS / Docker image / trial protocol:
- Agreed latency target or SLO:
- Published image full-SHA reference:
- Deployment workflow URL, deployment ID, and live status:
- Public HTTPS URL:
- `/health` result:
- `/ready` result:
- Public PvP smoke:
- Public PvAI smoke:
- Public History/reload smoke:
- Test game ID and production post-redeploy persistence result:
- Open risks / issue links:
- Independent reviewer and decision (GO / NO-GO):
- Timestamp and evidence author:

Never include secrets, access tokens, database credentials, private deploy hooks, or unredacted secret-bearing logs.

## 6. Go / no-go rule

Remain **BLOCKED / NO-GO** until all required P0 evidence is present for the same approved candidate and independently reviewed. In particular:

- A passing CI run, Docker build, PR E2E run, or disposable Compose restart is not a production deployment.
- Production publish/deploy, immutable image identity, public HTTPS health/readiness, public PvP/PvAI/History smoke, and production persistence after redeploy must each have their own evidence.
- Benchmark acceptance is incomplete until exact-SHA results, raw artifacts, Linux/Docker measurements, and the team's latency target/SLO decision are recorded.
- PR #35 must receive an explicit contract decision before merge; its described in-memory history implementation must not be represented as persisted History.

M5 records and audits evidence. M5 does not certify unexecuted deployment work on behalf of M1, M2, M3, or M4.

## 7. C2 database guard handover — 2026-10-29

**C2 database-guard gate: PASS for tested merge-validation SHA `4aa5a21baccdaa319aa4cd482b1a929badc7be01`.** The code now uses a shared pre-DDL validator in [`app/db/testing.py`](https://github.com/emt0147t/caroAI/blob/feature/m5-sprint4-qa/app/db/testing.py), called by both PostgreSQL test paths. It validates the explicit disposable marker, PostgreSQL backend, test-identifying database name, and rejects production/live-like names before engine creation/schema DDL.

Evidence:
- [CI #339](https://github.com/emt0147t/caroAI/actions/runs/40894014703) Python/lint job: **226 passed, 11 skipped, 1 warning**. [PostgreSQL acceptance job logs](https://github.com/emt0147t/caroAI/actions/runs/40894014703) show **15 passed, 0 skipped** and the explicit zero-skip guard passed.
- [`tests/test_database_guard.py`](https://github.com/emt0147t/caroAI/blob/feature/m5-sprint4-qa/tests/test_database_guard.py) exercises missing URL, missing/wrong marker, non-PostgreSQL URL, non-test DB name, production/live-like names, and a valid disposable target.
- CI #339 and Browser E2E #63 both ran against current PR head `27f232348151cf17fe447760dd8944e6b18d5ff9`; CI merge-validation SHA was `3275dae9090543ce979417708bcff862be16246a`, merging that head into base `138164803f3537d15ca90d9bc358f3f86528c4f3`.

The general suite's 11 skips are expected when PostgreSQL environment variables are absent; they are not PostgreSQL passes. The dedicated PostgreSQL job has its own zero-skip guard. [CI #339](https://github.com/emt0147t/caroAI/actions/runs/40894014703) and [Browser E2E #63](https://github.com/emt0147t/caroAI/actions/runs/40894014957) are now both complete with success on the current PR head. CI also passed Compose persistence, frontend checks, and Docker build; approved production publish/deploy was skipped.

Keep **BLOCKED / NO-GO** until benchmark acceptance, approved production image/deployment identity, public health/readiness and game-flow smoke, production persistence after redeploy, rollback evidence, PR #35 contract triage, and independent review are complete.


## 8. Explicit owner handoff for remaining release gates — 2026-10-29

The assignments below align with the existing Sprint 3 issue owners. They are recorded as a handoff request, not proof that the owners have acknowledged or completed the work.

| Gate | Directly responsible | Support / independent reviewer | Tracking and completion evidence |
|---|---|---|---|
| PR #35 persisted-History contract decision | **M1 Thành (@emt0147t)** | M5 documents QA impact; M3 confirms frontend contract | [PR #35](https://github.com/emt0147t/caroAI/pull/35), [Issue #23](https://github.com/emt0147t/caroAI/issues/23). Written decision based on actual diff and persistence contract. |
| AI tactical regression + Windows/Linux-Docker benchmark | **M2 Kiên (@KenKen106)** | M4 supplies Docker/CPU environment; M5 audits reproducibility | [Issue #28](https://github.com/emt0147t/caroAI/issues/28). Exact SHA, command, fixtures/trials, tactical outcomes, environment, raw CSV/JSON, median/p95 and agreed target/SLO. |
| Approved promotion, full-SHA image, live image identity | **M4 Vinh (@macvinh2007-sketch)** | **M1 Thành (@emt0147t)** as independent reviewer; M5 records | [Issue #30](https://github.com/emt0147t/caroAI/issues/30). Environment protections, approved source SHA, workflow, immutable image digest, deployment ID/status. |
| Public HTTPS health/readiness + PvP/PvAI/History smoke | **M3 Hiền (@NgocHein)** for browser tests; **M4 Vinh (@macvinh2007-sketch)** for deployment/health | M1 checks API/state correctness; M5 records | [Issues #29](https://github.com/emt0147t/caroAI/issues/29) and [#30](https://github.com/emt0147t/caroAI/issues/30). Public URL, source/image SHA, browser/version, health/readiness responses, test game IDs and artifacts. |
| Persistence after production redeploy | **M4 Vinh (@macvinh2007-sketch)** | M1 validates semantics; M5 independently checks evidence | [Issue #30](https://github.com/emt0147t/caroAI/issues/30). Designated non-destructive test game readable before/after redeploy, tied to live image SHA. |
| Rollback/redeploy runbook and exercise | **M4 Vinh (@macvinh2007-sketch)** | M1 independent reviewer; M5 evidence audit | [Issue #30](https://github.com/emt0147t/caroAI/issues/30). Steps, image/SHA, rollback trigger, migration/data risk, verification and exercise outcome. |
| Matrix, evidence reconciliation and final decision packet | **M5 Hiếu (@dyhieu-vu)** | Each owner provides own evidence; independent reviewer signs off | [Issue #31](https://github.com/emt0147t/caroAI/issues/31), [PR #39](https://github.com/emt0147t/caroAI/pull/39). No owner work is marked complete without evidence on the same approved candidate. |

### Handoff sequence

1. M1 records the PR #35 History contract decision.
2. M2 and M4 deliver benchmark/tactical evidence and the agreed latency target or SLO.
3. M4 prepares and promotes the approved candidate only after release preflight and independent M1 review.
4. M3/M4 run public health and game-flow smoke; M4 verifies persistence after redeploy and records rollback evidence.
5. M5 reconciles exact SHAs and evidence links; an independent reviewer makes the final GO/NO-GO decision.

No deadline is assigned without confirmation from the relevant owner. **Current status remains BLOCKED / NO-GO.** A passing CI run, PR E2E, or Compose restart does not replace any production gate.


## 9. C3 evidence reconciliation — latest PR head (2026-10-29)

The latest PR head is `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`. The earlier handover note saying no workflow runs were returned for this docs-only head is superseded by these verified runs:

- [CaroAI CI push #40896236338](https://github.com/emt0147t/caroAI/actions/runs/40896236338): **SUCCESS** on the exact latest head. Python/lint **226 passed, 11 skipped, 1 warning**; dedicated PostgreSQL acceptance **15 passed, 0 skipped**, with the zero-skip guard; Compose persistence, frontend regression and Docker image build succeeded. Production publish/deploy was skipped.
- [CaroAI CI pull-request run #40896239232](https://github.com/emt0147t/caroAI/actions/runs/40896239232): **SUCCESS** on the same head.
- [Browser E2E #40896239254](https://github.com/emt0147t/caroAI/actions/runs/40896239254): **13 Playwright tests passed** on the same head.

### Scoped acceptance decision

**C2 database guard: PASS / COMPLETE on latest PR head.** The dedicated PostgreSQL acceptance job has 15 passed and zero skipped, and the explicit zero-skip guard passed. General-suite skips remain skips, not passes. Compose and browser evidence are CI/PR evidence only.

**C3 evidence update and acceptance decision: IN PROGRESS.** Latest SHA and test-layer evidence have been reconciled and recorded. Overall release remains **BLOCKED / NO-GO** until the remaining T-12–T-17 production/benchmark gates, PR #35 History-contract decision, and independent review are complete. The successful Docker build did not publish/deploy an image; public HTTPS smoke and production persistence after redeploy remain unverified.

The evidence matrix is [docs/phase4-m5-qa-matrix.md](phase4-m5-qa-matrix.md). PR #39 remains open and unmerged.


## 10. C3 latest-head workflow verification — 2026-10-29

The latest PR #39 head `1d41eafac084910e6d30e3ed2e35c858f4337115` has now passed all three current-head workflow runs:

- [CaroAI CI push #40896984579](https://github.com/emt0147t/caroAI/actions/runs/40896984579) — **SUCCESS**.
- [CaroAI CI pull request #40896992335](https://github.com/emt0147t/caroAI/actions/runs/40896992335) — **SUCCESS**.
- [Frontend Browser E2E #40896992363](https://github.com/emt0147t/caroAI/actions/runs/40896992363) — **SUCCESS**.

Each run reports the same exact head SHA, `1d41eafac084910e6d30e3ed2e35c858f4337115`. The detailed counts (general suite 226 passed / 11 skipped / 1 warning; dedicated PostgreSQL 15 passed / 0 skipped; E2E 13 passed) are explicitly tied to the earlier verified C2 candidate `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`; do not assume those counts belong to the newer documentation SHA unless its job logs confirm them.

**C3 evidence-update checkpoint: COMPLETE. Release decision: BLOCKED / NO-GO.** The current PR/CI evidence is reconciled. Remaining release blockers are T-12 AI tactical regression and Linux/Docker benchmark artifacts; T-13 approved immutable published/live image identity; T-14 public HTTPS health/readiness; T-15 public PvP/PvAI/History smoke; T-16 production persistence after redeploy; T-17 rollback evidence; the explicit PR #35 persisted-History contract decision; and independent release review. These require the named owners' evidence and cannot be closed by passing CI or PR E2E alone.

PR #39 remains open and unmerged. This C3 checkpoint does not authorize a merge or production release.

## 11. Phase E deliverables and handoff snapshot — 2026-10-30

The Phase E documentation package is now present on feature/m5-sprint4-qa:

| Deliverable | Document | Status |
|---|---|---|
| 1. Phase 4 QA matrix | [phase4-m5-qa-matrix.md](phase4-m5-qa-matrix.md) | Maintained; Section 12 refreshes the exact current PR/CI head. |
| 2. QA baseline and workflow links | [phase4-m5-qa-matrix.md](phase4-m5-qa-matrix.md), Section 12 | Current PR-head push/PR CI and Browser E2E URLs recorded with exact SHA and scope. |
| 3. Regression/database acceptance report | [phase4-m5-qa-matrix.md](phase4-m5-qa-matrix.md), T-01–T-17 and Section 12 | CI, PostgreSQL zero-skip guard, Compose restart and Browser E2E distinguished by layer. |
| 4. Public smoke and post-redeploy persistence | [phase4-m5-d-evidence.md](phase4-m5-d-evidence.md), Sections 4 and 8–9 | NOT RUN / BLOCKED; no public URL, deployed image digest, deployment ID or same-game production read-back. |
| 5. Seven-minute demo runbook | [phase4-m5-e-demo-runbook.md](phase4-m5-e-demo-runbook.md) | Prepared from inspected API, Compose, migration and workflow code; unverified production steps are marked. |
| 6. Release sign-off | [phase4-m5-e-release-signoff.md](phase4-m5-e-release-signoff.md) | M5 recommendation BLOCKED / NO-GO; authorized approver fields intentionally remain blank. |
| 7. Issue closure recommendations | [phase4-m5-e-issue-triage.md](phase4-m5-e-issue-triage.md) | #23, #28, #29, #30 and #31 reviewed; no issue closed or modified. |
| 8. Failure triage | [phase4-m5-e-failure-triage.md](phase4-m5-e-failure-triage.md) | No confirmed failing job in latest workflow pair; warnings, skips and unrun release gates are classified separately. |

### Current exact-head workflow references

The current PR #39 head at this evidence checkpoint was 5ca2766f35a2ec54dba393e417074246683bdb60:

- [CaroAI CI push #40993815986](https://github.com/emt0147t/caroAI/actions/runs/40993815986) — SUCCESS.
- [CaroAI CI pull request #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096) — SUCCESS.
- [Frontend Browser E2E #40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081) — SUCCESS; [artifact #12950163434](https://github.com/emt0147t/caroAI/actions/runs/40993819081/artifacts/12950163434).
- The production publish/Render verification job in CI was skipped. No deployment is claimed.

### Remaining owner handoff

- **M2:** attach Sprint 3 tactical/benchmark evidence and raw CSV/JSON to Issue #28, or explicitly mark unrun items and reasons.
- **M1/team:** record the accepted/replaced latency target/SLO and the formal PR #35 History disposition.
- **M4 + M1:** supply approved release identity and deployment evidence only under release/change approval; do not deploy merely to satisfy the QA checklist.
- **M3:** execute public browser smoke only after M4 provides the approved URL and immutable image/source identity.
- **M4 + M1:** verify production same-game persistence after redeploy and rollback under approved change control.
- **M5:** reconcile new evidence when supplied; do not change NOT RUN/BLOCKED to PASS without the named evidence.

**Phase E documentation package: prepared. Overall Phase 4 release: BLOCKED / NO-GO.** This handover does not close Sprint 3 issues, Phase D gates, PR #35, or PR #39 and does not authorize production deployment.