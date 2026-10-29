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
