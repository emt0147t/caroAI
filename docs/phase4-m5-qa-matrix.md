# CaroAI Phase 4 — M5 QA/Test Evidence Matrix

> **Status:** Working evidence register; not release approval.
> **Prepared:** 2026-10-29
> **Owner:** M5 — Database, QA, Documentation / Release Evidence
> **Branch:** `feature/m5-sprint4-qa`
> **Baseline recorded in the Phase 4 audit:** `138164803f3537d15ca90d9bc358f3f86528c4f3`
> **CI evidence:** [CI run #299](https://github.com/emt0147t/caroAI/actions/runs/39994725661)
> **Browser E2E evidence:** [Browser E2E run #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162)
> **Release decision:** **BLOCKED / NO-GO**

This matrix records what has evidence, at which test layer, and what remains unverified. It intentionally does not rewrite the Sprint 3 record in [docs/sprint-3-qa-matrix.md](./sprint-3-qa-matrix.md).

## 1. Status and evidence rules

- A result applies only to the source SHA, environment, and workflow actually recorded for it.
- **PASSED** means the stated test layer passed; it does not imply production acceptance.
- **PR-ONLY** means pull-request validation evidence, not public or production evidence.
- **PARTIAL** means evidence exists but does not satisfy the complete acceptance criterion.
- **NOT RUN** means no execution evidence was identified in the reviewed records; it does not mean the feature failed.
- Do not combine counts from different commits. Re-run impacted checks when the release-candidate SHA changes.
- General Python test skips and the dedicated PostgreSQL acceptance job are separate: the 11 skips in the general suite are not PostgreSQL passes. CI #299's dedicated PostgreSQL acceptance job passed its zero-skip guard.
- Workflow logs referenced in this matrix were dated 2026-10-23. CI #299 ran on exact `develop` SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`. Browser E2E #49 ran on PR #38 merge-validation snapshot `a656439` with PR head `02b2ca64fba7ad8ec1387ca25738917bc6bc2ddc`. Reconfirm current runs and exact SHA before sign-off.
- Current PR #39 validation was inspected on 2026-10-29: CI #307 and Browser E2E #50 jobs succeeded. The Python job reported 218 passed / 11 skipped / 1 warning; the dedicated PostgreSQL job reported 15 passed / 0 skipped with its zero-skip guard; E2E #50 reported 13/13 passed. However, both current job logs print checkout commit `21505ad2541d5be6135ed84fc33697146cf75b8e`, and the GitHub commit endpoint did not resolve that SHA during C1. Do not silently equate it with PR head `44c37bb52f9e4e131f85e532482d39bc311c9f9c`; exact source-SHA linkage is an open acceptance item.
- Never store credentials, tokens, or production database URLs in this document.

## 2. Baseline snapshot

| Gate | Recorded result | Scope / limitation |
|---|---|---|
| `develop` SHA | `138164803f3537d15ca90d9bc358f3f86528c4f3` | Recorded merge commit for PR #38 at the audit point; verify branch head before release work |
| `main` SHA | `d444119d5eb757e364f904bb9eacddd27e14e507` | Observed behind `develop`; do not release from this stale snapshot without reconciliation |
| General Python suite, CI #299 | 218 passed, 11 skipped, 1 warning | Exact SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; general suite, not a substitute for dedicated PostgreSQL acceptance |
| PostgreSQL acceptance, CI #299 | 15 passed, 0 skipped; zero-skip guard passed | [Job log](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481); exact SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; 1 warning |
| Compose persistence, CI #299 | SUCCESS | Disposable Compose stack; API restart and persisted-state read-back covered |
| Browser E2E, run #49 | 13/13 Playwright tests passed | PR #38 merge-validation SHA `a656439` (full SHA visible in [job log](https://github.com/emt0147t/caroAI/actions/runs/39990335162/job/120540152992)); PR head `02b2ca64fba7ad8ec1387ca25738917bc6bc2ddc`; not production/live evidence; [Playwright artifact](https://github.com/emt0147t/caroAI/actions/runs/39990335162) |
| Current PR #39 CI #307 — Python tests/lint | **218 passed, 11 skipped, 1 warning** | [Job log](https://github.com/emt0147t/caroAI/actions/runs/40874711154/job/123450439620), run date 2026-10-29; log reports checkout commit `21505ad2541d5be6135ed84fc33697146cf75b8e`, which could not be resolved through the repository commit endpoint during C1. Treat counts as run evidence, but exact source-SHA linkage remains open. |
| Current PR #39 CI #307 — PostgreSQL acceptance | **15 passed, 0 skipped; zero-skip guard passed** | [Job log](https://github.com/emt0147t/caroAI/actions/runs/40874711154/job/123450439208); same unresolved checkout commit in job logs; disposable PostgreSQL acceptance only, not production. |
| Current PR #39 CI #307 — Compose persistence | SUCCESS | [Workflow #307](https://github.com/emt0147t/caroAI/actions/runs/40874711154); disposable Compose stack only. |
| Current PR #39 CI #307 — Frontend regression | SUCCESS | [Workflow #307](https://github.com/emt0147t/caroAI/actions/runs/40874711154); CI validation only. |
| Current PR #39 CI #307 — Docker build | SUCCESS | [Workflow #307](https://github.com/emt0147t/caroAI/actions/runs/40874711154); build-only, no publish/deploy. |
| Current PR #39 Browser E2E #50 | **13/13 Playwright tests passed** | [Job log](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883); 13 named tests cover History retry/reload, PvP, PvAI API, duplicate submit, HTTP 400/422/404, network recovery, AI retry, terminal lock, draw, and desktop/mobile viewports. PR-only; log's checkout commit SHA must be reconciled before declaring exact-SHA acceptance. |
| Production publish/deploy | SKIPPED | No production release evidence in these runs |
| Public HTTPS smoke | NOT RUN | No verified public `/health`, `/ready`, or game-flow smoke evidence located |
| Production persistence after redeploy | NOT RUN | Compose restart is not production redeploy evidence |

## 3. Acceptance matrix (T-01 to T-17)

| ID | Area | Acceptance criterion | Status | Owner / dependency | Evidence and limitation |
|---|---|---|---|---|---|
| T-01 | Create game + GET | Create a game; GET returns authoritative ID, mode, board and status | **PASSED at SQLite/API and PostgreSQL API acceptance layers** | M5 + M1 | [Portable suite](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165472) includes API create/read tests; [PostgreSQL acceptance job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481) ran `tests/postgres_suite.py` and `tests/test_database_postgres.py`: 15 passed, 0 skipped on SHA `138164803f3537d15ca90d9bc358f3f86528c4f3` |
| T-02 | Move ordering | Persisted moves have correct increasing move numbers and order | **PASSED at PostgreSQL repository/API acceptance layer** | M5 + M1 | [PostgreSQL acceptance job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481): 15 passed, 0 skipped on SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; `tests/postgres_suite.py` checks API move sequence and persisted move numbers; no production inference |
| T-03 | Human + AI move persistence | Human move and AI-produced move are persisted and read back | **PASSED for repository/API persistence; real AI engine integration not proven by PostgreSQL acceptance** | M5 + M1/M2 | [PostgreSQL acceptance job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481): 15 passed, 0 skipped on SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; `tests/postgres_suite.py` monkeypatches `run_ai_engine` with a deterministic fake move. [E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162) is PR-only on merge snapshot `a656439`; rerun on release candidate |
| T-04 | Win/draw/end state | Terminal status/result/winner/end time and move count persist; terminal board rejects further moves | **PASSED for X-win persistence; draw persistence is verified in portable SQLite tests, not separately in PostgreSQL acceptance** | M5 + M1 | PostgreSQL `tests/postgres_suite.py` covers X win/result/winner/end time and move count on SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; portable `tests/test_repository_persistence.py` includes draw persistence; E2E #49 terminal lock is PR-only on merge snapshot `a656439` |
| T-05 | DB write failure / rollback | Failed persistence write rolls back atomically without partial move/history | **PASSED in SQLite portable tests and PostgreSQL API acceptance** | M5 + M1 | `tests/test_repository_persistence.py` injects a service write failure and asserts no partial move; `tests/postgres_suite.py` injects a SQLAlchemy write failure and checks zero persisted moves plus unchanged game status. Both suites passed on SHA `138164803f3537d15ca90d9bc358f3f86528c4f3`; [Python job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165472), [PostgreSQL job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165481) |
| T-06 | Session/API restart | Data remains readable in a new session and after API restart in Compose | **PASSED in disposable Compose** | M5 + M4 | [Compose persistence job](https://github.com/emt0147t/caroAI/actions/runs/39994725661/job/120555165000); does not prove production persistence |
| T-07 | History after browser refresh | History is API/DB-backed and survives reload/new page | **PR-ONLY (E2E #49 and #50)** | M5 + M3/M1 | Historical [E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162) passed 13/13 on PR #38 snapshot `a656439`. Current [E2E #50 job log](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883) also passed 13/13, including History retry and a created game appearing in backend History after reload in a fresh page. Exact checkout SHA reconciliation remains open; neither run is public/production evidence. |
| T-08 | PvP happy path | Create PvP game, alternate X/O, enforce backend state and terminal lock | **PR-ONLY (E2E #49 and #50)** | M5 + M3/M1 | [E2E #50](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883) passed the PvP backend-authoritative alternating-moves test; source-SHA linkage still needs reconciliation. Repeat on approved candidate and public URL. |
| T-09 | PvAI happy path | Difficulty reaches real API; AI move comes from backend state; loading/disabled states work | **PR-ONLY (E2E #49 and #50)** | M5 + M2/M3/M1 | [E2E #50](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883) passed the PvAI real-API flow. This demonstrates frontend/backend flow with the CI app, not tactical strength, reproducible latency, or production AI quality; benchmark tracked separately in T-12. |
| T-10 | Duplicate submit / HTTP errors / lost response | Prevent duplicate moves; handle 400/422/404 and recover from network failure safely | **PR-ONLY (E2E #49 and #50)** | M5 + M3/M1 | [E2E #50](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883) passed duplicate-submit protection, HTTP 400/422/404 handling, network recovery and AI retry tests; artifact available from the workflow. Exact checkout SHA reconciliation remains open. |
| T-11 | Desktop/mobile layout | Board remains usable on desktop and narrow viewport | **PR-ONLY (E2E #49 and #50)** | M5 + M3 | [E2E #50](https://github.com/emt0147t/caroAI/actions/runs/40874711121/job/123450438883) passed the desktop/mobile viewport test; does not replace manual UX/accessibility review or public deployment smoke. Exact checkout SHA reconciliation remains open. |
| T-12 | AI tactical regression + benchmark | Tactical cases pass; reproducible Windows and Linux/Docker benchmark artifacts and latency target/SLO are documented | **PARTIAL** | M2 executes; M5 audits evidence | [Benchmark report](https://github.com/emt0147t/caroAI/blob/develop/reports/ai-benchmark.md), [PR #36](https://github.com/emt0147t/caroAI/pull/36); Sprint 4 benchmark remains NOT RUN in recorded baseline; Linux/Docker results and raw artifacts unverified; clarify whether p95 ≤ 2,000 ms is an SLO or target |
| T-13 | Release SHA / image identity | Lock release candidate SHA; publish image tagged by full SHA; live service identity matches candidate | **PARTIAL** | M4 executes; M5 verifies; M1 approves | CI #299 and [M4 runbook](https://github.com/emt0147t/caroAI/blob/develop/docs/m4-release-operations.md); CI passed but publish/deploy was skipped; candidate SHA/image identity not verified |
| T-14 | Public HTTPS health/readiness | Public HTTPS `/health` and `/ready` return expected successful responses after deployment | **NOT RUN** | M4 executes; M5 records | No verified public run located; blocked on approved deployment and URL/access |
| T-15 | Public PvP/PvAI/History smoke | Public app supports PvP, PvAI, History and reload without fabricated state/errors | **NOT RUN** | M3/M4 execute; M5 records; M1 signs off | Record public URL/environment, browser version, game IDs, screenshots/artifacts, result and source SHA |
| T-16 | Production persistence after redeploy | Identified test game's moves/history remain readable after production restart/redeploy | **NOT RUN** | M4 executes; M5 verifies; M1 signs off | No production redeploy evidence; Compose restart does not satisfy this criterion; use an approved test game and avoid destructive tests |
| T-17 | Rollback/redeploy instructions | Runbook identifies image/SHA, migration/data risks, rollback trigger, steps, verification and owner; exercise recorded if required | **PARTIAL** | M4 documents/executes; M5 verifies; M1 reviews | [M4 runbook](https://github.com/emt0147t/caroAI/blob/develop/docs/m4-release-operations.md) exists; successful rollback/redeploy exercise not evidenced |

## 4. Cross-cutting QA guardrails

1. **SHA integrity:** never combine test counts across SHAs; rerun impacted gates if the candidate changes.
2. **PostgreSQL safety:** destructive database tests must use a disposable DB/schema and fail closed without an explicit disposable-database marker.
3. **Evidence layers:** distinguish unit, service/API, disposable PostgreSQL, Compose restart, browser E2E, local manual smoke, public smoke, and production persistence after redeploy.
4. **Production evidence:** CI success, Docker build, PR E2E and Compose persistence are not evidence of production deployment.
5. **Secrets:** never commit or attach secrets in logs, screenshots, issue comments or artifacts.
6. **Issue closure:** do not recommend closing Issues #23, #28, #29, #30 or #31 until their acceptance criteria are evidenced or the team explicitly accepts a documented non-applicability.
7. **Independent sign-off:** release reviewer should not be the author of the change being signed off.

## 5. Dependencies and next actions

| Priority | Action | Owner | Exit evidence |
|---|---|---|---|
| P0 | Triage whether PR #35 conflicts with persisted History contract; decide fix/close/update | M1; M5 documents QA risk | Written decision linked to actual diff and persistence contract |
| P0 | Run AI tactical regression and benchmark on exact candidate and Linux/Docker | M2 + M4; M5 verifies | Full SHA, OS/CPU/container, fixture/trial method, raw CSV/JSON, tactical results, explicit SLO/target |
| P0 | Production preflight/promotion using approved Environment and reviewer | M4 + M1 | Required reviewers/secrets/branch restrictions verified; no dispatch from stale `main` |
| P0 | Run public HTTPS and PvP/PvAI/History smoke after promotion | M3/M4 execute; M5 records | URL, environment, browser/version, SHA, workflow/artifact and outcomes |
| P0 | Verify approved test-game persistence after production redeploy | M4 executes; M5 verifies; M1 signs off | Before/after game ID, move/history evidence, live image SHA |
| P1 | Complete seven-minute demo checklist and failure-triage records | M5 + M1–M4 | Honest script that states unavailable features and open risks |
| P1 | Prepare issue closure recommendations for #23/#28/#29/#30/#31 | M5; issue owners confirm | Each issue mapped to its own acceptance evidence; no blanket closure |
| P1 | Produce final one-page release sign-off | M5; independent reviewer approves | Candidate SHA, CI, PostgreSQL, E2E, benchmark, public smoke, post-redeploy persistence, risks and GO/NO-GO |

## 6. Current release decision

**BLOCKED / NO-GO.**

Reasons:
- Production publish/deploy and live image identity are not evidenced.
- Public HTTPS and public PvP/PvAI/History smoke are not evidenced.
- Production persistence after redeploy is not evidenced.
- Phase 4 benchmark acceptance and Linux/Docker artifacts remain incomplete.
- PR #35 requires explicit contract triage before any merge decision.

This matrix is an evidence register, not release approval. Keep the release blocked until the P0 evidence is complete and independently reviewed.


## 7. C1 regression-acceptance checkpoint — 2026-10-29

This checkpoint records fresh CI/E2E evidence for the current PR merge-validation candidate. It does not approve production release.

| Gate | Current evidence | Exact scope and limitation |
|---|---|---|
| PR #39 candidate | Head `bf0f8e06c668eb30c9e939ad87ac12ed049c2626`; base `develop` at `138164803f3537d15ca90d9bc358f3f86528c4f3`; merge-validation SHA `34cf32d8c97377d37c2b468785e2a01c03f469bf`. [PR #39](https://github.com/emt0147t/caroAI/pull/39) | Documentation-only PR; application code and production configuration were not changed. |
| CaroAI CI #321 | [Workflow run](https://github.com/emt0147t/caroAI/actions/runs/40892411531) — **SUCCESS** | Logs explicitly show checkout of `refs/remotes/pull/39/merge` and `HEAD is now at 34cf32d`, merging PR head `bf0f8e0` into base `1381648`. Python/lint: 218 passed, 11 skipped, 1 warning. Frontend checks, Compose persistence after API restart, Compose config validation and Docker build passed. |
| PostgreSQL acceptance in CI #321 | [Workflow run](https://github.com/emt0147t/caroAI/actions/runs/40892411531) — **15 passed, 0 skipped** | Dedicated zero-skip guard passed. Disposable CI PostgreSQL only; not production post-redeploy evidence. |
| Frontend Browser E2E #55 | [Workflow run](https://github.com/emt0147t/caroAI/actions/runs/40892411540) — **13 passed** | Logs explicitly show checkout of the same PR #39 merge-validation SHA `34cf32d8c97377d37c2b468785e2a01c03f469bf`. Real API + frontend in disposable Compose; PR-only, not public/production smoke. |
| Production publish/deploy | **SKIPPED** in CI #321 | No approved production promotion, published immutable image, deployment identity, or live service verification was produced. |

### C1 closure decision

- **C1 PR-validation gate: PASS for PR #39 merge-validation SHA `34cf32d8c97377d37c2b468785e2a01c03f469bf`.** CI #321 and Browser E2E #55 both completed successfully on that exact merge-validation SHA. The earlier CI #307 / E2E #50 logs reported a different checkout commit and must not be cited as proof for PR head `44c37bb`.
- **C1 application-code regression after a new application-code change: NOT EXERCISED by PR #39.** The PR is documentation-only. These runs prove the documented PR candidate's workflow gates, not a new application build or runtime change.
- **C1 is closed only for the scoped QA-matrix/documentation PR validation.** It does not close C2 database guard, benchmark acceptance, production release acceptance, or owner-dependent sign-offs.
- **Release remains BLOCKED / NO-GO.** T-12 benchmark acceptance, T-13 published image identity, T-14 public HTTPS health/readiness, T-15 public game-flow smoke, T-16 production persistence after redeploy, T-17 rollback exercise, and the explicit PR #35 History-contract decision remain unresolved until their own evidence is recorded.
- **PR #35** remains a separate draft PR targeting `main`, while PR #39 targets `develop`. Its in-memory `GET /api/history` implementation must not be treated as satisfying persisted History. M1 / the API owner must record the contract decision; M5 must not unilaterally claim this cross-owner acceptance is complete.

Evidence links:
- [CaroAI CI #321](https://github.com/emt0147t/caroAI/actions/runs/40892411531)
- [Browser E2E #55](https://github.com/emt0147t/caroAI/actions/runs/40892411540)
- [PR #39](https://github.com/emt0147t/caroAI/pull/39)
- [PR #35](https://github.com/emt0147t/caroAI/pull/35)

## 8. C2 database guard audit — 2026-10-29

The guard is now covered by a shared validation helper and explicit negative-path regression tests.

| Guard control | Evidence | Assessment |
|---|---|---|
| Dedicated PostgreSQL service | CI #339 uses a disposable `postgres:15-alpine` service with a health check and job-scoped test credentials. [Workflow](https://github.com/emt0147t/caroAI/actions/runs/40894014703) | **PASS for CI disposable environment** |
| Shared pre-DDL target validation | [`app/db/testing.py`](https://github.com/emt0147t/caroAI/blob/feature/m5-sprint4-qa/app/db/testing.py) validates the URL, explicit disposable marker, PostgreSQL backend, test-identifying DB name, and rejects production/live-like names before engine/schema creation. Both PostgreSQL test paths call this helper. | **PASS by code review + tests** |
| Negative-path regression coverage | [`tests/test_database_guard.py`](https://github.com/emt0147t/caroAI/blob/feature/m5-sprint4-qa/tests/test_database_guard.py) tests missing URL, missing/wrong marker, SQLite URL, non-test DB name, production/live-like DB names, and a valid disposable target. | **PASS** |
| Dedicated PostgreSQL acceptance and skip guard | CI #339 PostgreSQL job [logs](https://github.com/emt0147t/caroAI/actions/runs/40894014703) report **15 passed, 0 skipped** and print `PostgreSQL acceptance suite completed with zero skipped tests.` | **PASS** |
| General suite including guard regression tests | CI #339 Python/lint job [logs](https://github.com/emt0147t/caroAI/actions/runs/40894014703) reports **226 passed, 11 skipped, 1 warning**. The 11 skips are the expected PostgreSQL fixture skips in the general suite, not PostgreSQL acceptance. | **PASS for general suite; skips remain skips** |
| Exact tested source | CI #339 and Browser E2E #63 both ran against PR head `27f232348151cf17fe447760dd8944e6b18d5ff9` and merge-validation SHA `3275dae9090543ce979417708bcff862be16246a`, merging that head into base `138164803f3537d15ca90d9bc358f3f86528c4f3`. | **PASS for current PR head and merge candidate** |

### C2 decision

**C2 database-guard gate: PASS, with PR-wide CI/E2E confirmation on current head.** [CI #339](https://github.com/emt0147t/caroAI/actions/runs/40894014703) and [Browser E2E #63](https://github.com/emt0147t/caroAI/actions/runs/40894014957) both completed successfully on PR head `27f232348151cf17fe447760dd8944e6b18d5ff9`; CI includes PostgreSQL acceptance with zero skips, general suite including the negative-path guard tests, Compose persistence, frontend checks, and Docker image build. Production publish/deploy was skipped.

**Release remains BLOCKED / NO-GO.** C2 does not close benchmark, approved production deployment/image identity, public smoke, production post-redeploy persistence, rollback, PR #35 contract triage, or independent review gates.


## 9. Release-gate owner assignment and execution queue — 2026-10-29

This is the operational owner map for the remaining release gates. Assignments follow the existing Sprint 3 ownership records; **owner acknowledgement and execution evidence are still required**. This document does not imply that an owner has accepted a new deadline or that a gate has passed.

| Order | Gate / deliverable | Accountable execution owner | Required support / independent check | Tracking | Required evidence to close |
|---|---|---|---|---|---|
| 1 | PR #35 History-contract triage | **M1 Thành (@emt0147t)** | M5 records the risk; M3 confirms UI/API expectation | [PR #35](https://github.com/emt0147t/caroAI/pull/35), [Issue #23](https://github.com/emt0147t/caroAI/issues/23) | Written decision against actual PR diff and persisted History contract; explicit fix/close/update decision. Do not merge in-memory History as DB-backed. |
| 2 | AI tactical regression + reproducible benchmark, including Linux/Docker | **M2 Kiên (@KenKen106)** | M4 provides/validates Docker CPU environment; M5 audits artifacts | [Issue #28](https://github.com/emt0147t/caroAI/issues/28), [T-12](#acceptance-matrix-t-01-to-t-17) | Exact full source SHA, command, fixtures/trial protocol, all supported difficulties, tactical outcomes, environment/CPU/container, raw CSV/JSON, median/p95, report, and team decision on p95 ≤ 2,000 ms as target or SLO. |
| 3 | Release preflight, immutable image publication, deployment and live image identity | **M4 Vinh (@macvinh2007-sketch)** | **M1 Thành (@emt0147t)** performs independent approval/review; M5 records | [Issue #30](https://github.com/emt0147t/caroAI/issues/30), [T-13](#acceptance-matrix-t-01-to-t-17) | Approved source branch/SHA, Environment protection evidence, successful promotion workflow, registry image tagged by full SHA/digest, deployment ID/status and live service identity. Do not dispatch from stale `main`. |
| 4 | Public HTTPS health/readiness and public PvP/PvAI/History smoke | **M3 Hiền (@NgocHein) for browser flows; M4 Vinh (@macvinh2007-sketch) for deployment/health access** | M1 signs off API/state correctness; M5 records results | [Issue #29](https://github.com/emt0147t/caroAI/issues/29), [Issue #30](https://github.com/emt0147t/caroAI/issues/30), [T-14](#acceptance-matrix-t-01-to-t-17), [T-15](#acceptance-matrix-t-01-to-t-17) | Public URL/environment, deployed source and image SHA, timestamp, browser/version, `/health` and `/ready` results, PvP/PvAI/History+reload outcomes, game IDs and redacted artifacts. |
| 5 | Production persistence after approved redeploy | **M4 Vinh (@macvinh2007-sketch)** | M1 validates application/API semantics; M5 independently verifies evidence | [Issue #30](https://github.com/emt0147t/caroAI/issues/30), [T-16](#acceptance-matrix-t-01-to-t-17) | Approved non-destructive test game; capture game ID and moves/history before and after redeploy; record deployed image SHA and successful read-back. Compose restart alone does not close this gate. |
| 6 | Rollback/redeploy runbook and exercise | **M4 Vinh (@macvinh2007-sketch)** | M1 independent reviewer; M5 checks evidence completeness | [Issue #30](https://github.com/emt0147t/caroAI/issues/30), [T-17](#acceptance-matrix-t-01-to-t-17) | Runbook includes immutable image/SHA, trigger, steps, migration/data risks, verification and owner; attach exercise result or clearly mark exercise not run if not approved. |
| 7 | Evidence reconciliation, QA matrix, final GO/NO-GO package | **M5 Hiếu (@dyhieu-vu)** | Each gate owner supplies evidence; independent reviewer must not be the author of the release change | [Issue #31](https://github.com/emt0147t/caroAI/issues/31), PR #39 | Evidence URLs and exact SHA for every gate; status labels distinguish PASS/PARTIAL/NOT RUN; independent reviewer records explicit decision. M5 cannot self-certify another owner's execution. |

### Execution order and control

1. **M1 decides PR #35 History contract** and the team agrees on the target release candidate; record the decision before considering PR #35 for merge.
2. **M2 + M4 complete T-12 benchmark evidence** on the named candidate and agree the latency target/SLO.
3. **M4 + independent M1 reviewer complete release preflight and T-13**. No public smoke should be claimed before a deployment is identified.
4. **M3 + M4 execute T-14/T-15**, then M4 executes T-16 after an approved redeploy; M5 captures and checks the evidence.
5. **M4 completes T-17 rollback evidence**, then M5 assembles the final packet for independent review.

No target dates are invented here because the repository evidence does not contain owner-approved dates. The owner map is documented, but acknowledgement, implementation and acceptance remain outstanding until the corresponding evidence is linked. Release remains **BLOCKED / NO-GO**.


## 10. C3 evidence reconciliation and scoped acceptance decision — 2026-10-29

### Exact latest-head evidence

The previous note that no workflows existed for the latest docs-only head is superseded by the following completed runs. All listed pull-request workflows identify the same current PR #39 head SHA: `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`.

| Gate | Current run / result | Exact scope and interpretation |
|---|---|---|
| PR head | `006354cbdd76b38cc8c78e9d9d2806f2ee39b095` | Current head of [PR #39](https://github.com/emt0147t/caroAI/pull/39), targeting `develop` at `138164803f3537d15ca90d9bc358f3f86528c4f3`. |
| CaroAI CI — push | [Run #40896236338](https://github.com/emt0147t/caroAI/actions/runs/40896236338) — **SUCCESS** | Run head SHA matches the latest PR head. Frontend regression, PostgreSQL acceptance, Python tests/lint, Compose persistence and Docker image build succeeded. Production publish/deploy job was skipped. |
| CaroAI CI — pull request | [Run #40896239232](https://github.com/emt0147t/caroAI/actions/runs/40896239232) — **SUCCESS** | Pull-request validation for the same head SHA. |
| General Python tests/lint | **226 passed, 11 skipped, 1 warning** | [Job log](https://github.com/emt0147t/caroAI/actions/runs/40896236338/job/123525982635). Skips are not passes and do not replace dedicated PostgreSQL acceptance. Warning includes Starlette/httpx TestClient deprecation. |
| PostgreSQL service/API/migration acceptance | **15 passed, 0 skipped**; explicit zero-skip guard printed | [Job log](https://github.com/emt0147t/caroAI/actions/runs/40896236338/job/123525982538). Disposable CI PostgreSQL; not production data or production redeploy evidence. |
| Compose persistence after API restart | **SUCCESS** | [CI run](https://github.com/emt0147t/caroAI/actions/runs/40896236338). Disposable Compose environment only. |
| Frontend syntax/regression | **SUCCESS** | [CI run](https://github.com/emt0147t/caroAI/actions/runs/40896236338). |
| Docker image build | **SUCCESS — build only** | [CI run](https://github.com/emt0147t/caroAI/actions/runs/40896236338). No publish or deploy. |
| Browser E2E | **13 passed** | [Run #40896239254](https://github.com/emt0147t/caroAI/actions/runs/40896239254); exact head SHA matches `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`. Playwright artifact uploaded. PR/CI environment only. |
| Approved production publish / Render verification | **SKIPPED** | No public deployment, immutable live image identity, public health/readiness, public game-flow smoke or post-redeploy production persistence evidence. |

### C2 decision at the latest PR head

**C2 — DATABASE GUARD: PASS / COMPLETE for the tested PR candidate**, including the latest PR head `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`. The latest-head CI has a successful dedicated PostgreSQL job with 15 passed / 0 skipped and an explicit zero-skip guard; the shared fail-closed target validator and negative-path guard tests are included in the passing general suite. Compose persistence and Browser E2E also pass on the latest PR head.

This decision is scoped to C2's database guard and PR/CI acceptance criteria. It does **not** mean that every Phase 4 release gate is complete or that production is approved.

### C3 status and acceptance decision

**C3 — EVIDENCE UPDATE & ACCEPTANCE DECISION: IN PROGRESS.** This checkpoint reconciles the latest head SHA, exact workflow URLs, pass/skip counts, test layers and evidence limitations. The scoped decision is:
- C1 scoped regression/PR validation: PASS.
- C2 database guard: PASS / COMPLETE on the latest PR head.
- Overall release acceptance: **BLOCKED / NO-GO**.

C3 remains in progress until the remaining owner-dependent gates have their own evidence and are reconciled against the approved release candidate: T-12 AI tactical benchmark and Linux/Docker artifacts; T-13 approved release SHA and immutable published/live image identity; T-14 public HTTPS health/readiness; T-15 public PvP/PvAI/History smoke; T-16 production persistence after redeploy; T-17 rollback evidence; PR #35 persisted-History contract decision; independent review. Do not infer production success from the successful CI jobs above.

Evidence:
- [Latest-head CI push run](https://github.com/emt0147t/caroAI/actions/runs/40896236338)
- [Latest-head CI PR run](https://github.com/emt0147t/caroAI/actions/runs/40896239232)
- [Latest-head Browser E2E](https://github.com/emt0147t/caroAI/actions/runs/40896239254)
- [PR #39](https://github.com/emt0147t/caroAI/pull/39)


## 11. C3 checkpoint update — latest documentation head validated (2026-10-29)

This addendum supersedes the earlier note that workflows for the latest documentation head were still pending. All three required workflows have now completed successfully against exact PR head `1d41eafac084910e6d30e3ed2e35c858f4337115`:

| Gate | Run | Result |
|---|---|---|
| CaroAI CI — push | [Run #40896984579](https://github.com/emt0147t/caroAI/actions/runs/40896984579) | **SUCCESS**; run head SHA matches `1d41eafac084910e6d30e3ed2e35c858f4337115` |
| CaroAI CI — pull request | [Run #40896992335](https://github.com/emt0147t/caroAI/actions/runs/40896992335) | **SUCCESS**; run head SHA matches the same SHA |
| Frontend Browser E2E | [Run #40896992363](https://github.com/emt0147t/caroAI/actions/runs/40896992363) | **SUCCESS**; run head SHA matches the same SHA |

The workflows validate the latest documentation/QA candidate. Detailed test counts and the dedicated PostgreSQL zero-skip result remain documented under the earlier verified C2 checkpoint on `006354cbdd76b38cc8c78e9d9d2806f2ee39b095`; do not attribute those exact counts to the newer SHA unless confirmed in its job logs. The current-head workflow conclusions are successful, but production publish/deploy remains unverified.

### C3 acceptance checkpoint

**C3 evidence reconciliation and acceptance decision: COMPLETE for the current PR/CI evidence checkpoint.** The exact latest head and its push CI, PR CI, and Browser E2E outcomes are recorded above. The explicit acceptance decision remains **BLOCKED / NO-GO for release** because the owner-dependent gates below have not been evidenced: T-12 benchmark/tactical regression; T-13 approved release SHA and immutable live image identity; T-14 public HTTPS health/readiness; T-15 public PvP/PvAI/History smoke; T-16 production persistence after redeploy; T-17 rollback evidence; PR #35 persisted-History contract decision; and independent release review.

This closes the M5 C3 evidence-update checkpoint only; it does not close the production release gates or authorize merging/deployment.

## 12. Phase E baseline refresh — current PR #39 evidence (2026-10-30)

> This addendum supersedes stale current-head pointers above for the exact SHA recorded here. Historical runs and counts remain historical and must not be reassigned to this SHA.

| Gate | Exact source SHA | Workflow / result | Scope and limitation |
|---|---|---|---|
| PR #39 head | 5ca2766f35a2ec54dba393e417074246683bdb60 | [PR #39](https://github.com/emt0147t/caroAI/pull/39), base develop | OPEN / UNMERGED at the time of this check. |
| CaroAI CI — push | 5ca2766f35a2ec54dba393e417074246683bdb60 | [Run #40993815986](https://github.com/emt0147t/caroAI/actions/runs/40993815986) — SUCCESS | CI on exact PR head. |
| CaroAI CI — pull request | 5ca2766f35a2ec54dba393e417074246683bdb60 | [Run #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096) — SUCCESS | Frontend regression, Python tests/lint, dedicated PostgreSQL acceptance/zero-skip guard, Compose persistence and Docker build jobs succeeded. Production publish/Render verification was SKIPPED. |
| Browser E2E — pull request | 5ca2766f35a2ec54dba393e417074246683bdb60 | [Run #40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081) — SUCCESS | Browser setup, version capture, real API/frontend startup, test execution, artifact upload and teardown succeeded. |
| Browser artifact | Same SHA as above | [Artifact #12950163434](https://github.com/emt0147t/caroAI/actions/runs/40993819081/artifacts/12950163434) | PR/CI artifact only; not a public deployment trace. |
| PostgreSQL acceptance | Same SHA as above | PostgreSQL service/API/migration acceptance job succeeded; explicit zero-skip guard succeeded | Disposable PostgreSQL service only. Do not infer production DB state. |
| Compose persistence after API restart | Same SHA as above | Compose API/database persistence after restart job succeeded | Disposable Compose DB; creates game/move, restarts API, reads the same game and History back. Not production redeploy. |
| Docker image build | Same SHA as above | Docker image build job succeeded | Build only. No registry publication or Render deployment. |
| Public smoke / production persistence / rollback | N/A | NOT RUN / BLOCKED | No approved public URL, published image digest, deployment ID, same-game production before/after read-back, or rollback evidence. |

### Baseline and test-count interpretation

- Current PR-head workflows above have verified SUCCESS conclusions and exact SHA linkage. Job metadata confirms the PostgreSQL zero-skip guard, Compose persistence and Browser E2E steps succeeded.
- Do not transfer the detailed 226 passed / 11 skipped / 1 warning general-suite count, 15 passed / 0 skipped PostgreSQL count, or 14 passed / 0 failed Browser E2E count from earlier exact SHAs to this SHA unless the corresponding current-run logs are explicitly inspected. Current run-level evidence is SUCCESS; this matrix does not invent new counts.
- The 11 general Python-suite skips from the earlier detailed run are separate from the dedicated PostgreSQL suite, whose explicit zero-skip guard passed.
- The CI production publish/Render job was skipped by its approval/ref condition. This is not a failed deployment; it confirms production deployment was not performed in this run.
- Current code inspection confirms versioned migration files and runner exist, and /health is liveness while /ready executes a DB query. See [database operations](../database/README.md).

### Phase E document set

- [Seven-minute demo runbook](phase4-m5-e-demo-runbook.md)
- [Issue triage and closure recommendations](phase4-m5-e-issue-triage.md)
- [Release sign-off record](phase4-m5-e-release-signoff.md)
- [Failure triage register](phase4-m5-e-failure-triage.md)
- [M5 handover](phase4-m5-handover.md)

**Current release disposition remains BLOCKED / NO-GO.** These documents complete M5's current documentation and recommendation package; they do not close M2/M3/M4-owned gates, PR #35, or authorize release.

## 13. Post-review develop sync and final validation checkpoint — 2026-10-31

### Branch synchronization and conflict resolution

- PR #39 branch `feature/m5-sprint4-qa` was 13 commits behind `develop`; the branch is now synchronized with the reviewed develop baseline. The merge commit `3e0b6d314737fd415239083045cef7a61468aa1b` has `develop` commit `914ba088a8753473c406f8870f6546ad44c38074` and prior PR head `79560a5131523493dbbfb4956ec7c1b78299f46c` as parents.
- `.github/workflows/frontend-e2e.yml`: retained baseline/candidate Compose screenshot capture and visual-evidence artifact upload; added Playwright/Chromium version recording to `evidence/browser-versions.txt`.
- `tests/e2e/game.spec.cjs`: retained 360/390/1280px responsive checks and body `scrollWidth`; retained the difficulty payload assertion and O-win terminal-state test.
- The first E2E attempt on merge SHA `3e0b6d3` exposed a misplaced difficulty assertion (23/24 passed). It was moved into the PvAI test in commit `50641a5f5a761474b80f5245fe29ece8f94fa8fd`; the final E2E run below passed 24/24.

### Exact-SHA validation results

| Evidence | Exact source SHA | Result |
|---|---|---|
| PR #39 head | `50641a5f5a761474b80f5245fe29ece8f94fa8fd` | OPEN / UNMERGED; GitHub reports mergeable; `develop` behind count = 0 |
| CaroAI CI — pull request | [Run #41220665617](https://github.com/emt0147t/caroAI/actions/runs/41220665617) | **SUCCESS** — Python/lint, frontend regression, PostgreSQL acceptance, Compose persistence and Docker image build passed; production publish/Render job SKIPPED |
| CaroAI CI — push | [Run #41220661758](https://github.com/emt0147t/caroAI/actions/runs/41220661758) | **SUCCESS** on the same SHA |
| Frontend Browser E2E | [Run #41220665448](https://github.com/emt0147t/caroAI/actions/runs/41220665448) | **24/24 passed** on the same SHA; baseline/candidate Compose startup, screenshot capture, artifact upload and teardown succeeded |
| General Python suite | Same SHA; PR CI #41220665617 | **228 passed, 11 skipped, 1 warning**. General-suite skips are separate from the dedicated PostgreSQL zero-skip acceptance gate. |
| PostgreSQL acceptance | Same SHA; PR CI job | **15 passed, 0 skipped**; explicit zero-skipped guard passed |
| Compose persistence | Same SHA; PR CI job | **PASS** — create game/move, restart API container, read the same game and History back |
| Docker image build | Same SHA; PR CI job | **PASS — build only**, no registry publication or deployment |
| Browser/runtime | Same SHA; Browser E2E job | Playwright **1.56.1**; Chromium **141.0.7390.37** |
| Playwright/visual artifact | Same SHA | [Artifact #13049848098](https://github.com/emt0147t/caroAI/actions/runs/41220665448/artifacts/13049848098) |

### Remaining release disposition

- The approved production publish / Render verification job was **SKIPPED** by its event/ref/approval condition. This is not a failed deployment and is not deployment evidence.
- T-12 through T-17 remain **BLOCKED / NOT VERIFIED** until their respective owners provide independent evidence. The persisted-History contract / PR #35 decision remains **PENDING M1/maintainers**.
- **PR #39 is OPEN / UNMERGED.** This validation does not approve or merge the PR.
- **Overall release remains BLOCKED / NO-GO.** CI, disposable PostgreSQL, Compose restart, Docker build and Browser E2E do not replace public HTTPS smoke, production post-redeploy persistence, immutable live image identity or rollback evidence.
