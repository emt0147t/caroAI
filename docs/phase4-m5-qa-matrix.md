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
| T-07 | History after browser refresh | History is API/DB-backed and survives reload/new page | **PR-ONLY** | M5 + M3/M1 | [E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162), PR merge snapshot `a656439`, PR head `02b2ca64fba7ad8ec1387ca25738917bc6bc2ddc`; Playwright artifact available; repeat on release candidate and public deployment |
| T-08 | PvP happy path | Create PvP game, alternate X/O, enforce backend state and terminal lock | **PR-ONLY** | M5 + M3/M1 | [E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162) passed on PR merge snapshot `a656439` (PR head `02b2ca64fba7ad8ec1387ca25738917bc6bc2ddc`); repeat on candidate and public URL |
| T-09 | PvAI happy path | Difficulty reaches real API; AI move comes from backend state; loading/disabled states work | **PR-ONLY** | M5 + M2/M3/M1 | [E2E #49](https://github.com/emt0147t/caroAI/actions/runs/39990335162) passed on PR merge snapshot `a656439`; benchmark tracked separately in T-12 |
| T-10 | Duplicate submit / HTTP errors / lost response | Prevent duplicate moves; handle 400/422/404 and recover from network failure safely | **PR-ONLY** | M5 + M3/M1 | E2E #49 on PR merge snapshot `a656439`; [Playwright artifact](https://github.com/emt0147t/caroAI/actions/runs/39990335162); rerun on candidate |
| T-11 | Desktop/mobile layout | Board remains usable on desktop and narrow viewport | **PR-ONLY** | M5 + M3 | E2E #49 passed 13/13 on PR merge snapshot `a656439`; does not replace manual UX/accessibility review |
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
