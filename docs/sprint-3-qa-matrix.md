# Sprint 3 QA Matrix — M5

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Baseline SHA: 2dd55cda274d7112e6d3244a4b457768178e98f8
- Baseline result: 178 passed, 11 skipped, 1 warning
- Baseline environment: local Windows; exact Python version not recorded
- PostgreSQL baseline: NOT RUN; TEST_DATABASE_URL was not configured
- Matrix documentation commit: see branch history; the matrix was committed and then clarified in subsequent commits.
- Current implementation audit: GameService on this branch stores games in an in-memory dictionary; app/db/repository.py is a placeholder. Persistence acceptance criteria are therefore NOT RUN / BLOCKED on this branch.
- CI audit: .github/workflows/ci-cd.yml has frontend, test/lint, and Docker build jobs, but no dedicated PostgreSQL job or PostgreSQL service/env configuration.
- Important: historical results are not proof of a pass on the current branch.
- Rule: SKIPPED and NOT RUN are not PASS. A source-code audit is not a runtime test.

## Status definitions

- PASSED: the exact test/smoke check ran successfully on the recorded SHA and environment.
- FAILED: the check ran and failed.
- SKIPPED: the runner discovered the check but did not execute it; record the reason.
- NOT RUN: no execution evidence is available.
- BLOCKED: a dependency or missing implementation prevents a meaningful run; do not treat this as PASS.

## Evidence matrix

| ID | Area | Acceptance evidence | Status | Owner / dependency | Evidence |
|---|---|---|---|---|---|
| QA-01 | Game rules | Existing regression suite | BASELINE SUITE PASSED; category-specific result not isolated | M5 | Baseline SHA above; 178 tests passed overall |
| QA-02 | AI | AI integration/regression tests | BASELINE SUITE PASSED; category-specific result not isolated | M2/M5 | Baseline run; detailed test names/results not captured |
| QA-03 | API regression | Existing API suite | BASELINE SUITE PASSED; category-specific result not isolated | M1/M5 | Baseline SHA above; 178 tests passed overall |
| QA-04 | Service/API persistence | Create game, make moves, commit, then read through a new session/service/API | BLOCKED / NOT RUN on this branch | M1 implementation; M5 tests | app/services/game_service.py uses an in-memory dict; app/db/repository.py is a placeholder |
| QA-05 | AI move persistence | Persist and read back an AI move | BLOCKED / NOT RUN on this branch | M1/M2/M5 | In-memory GameService on this branch; PR #32 test evidence is separate and used mocked AI |
| QA-06 | Terminal win persistence | Persist status, winner/result and ended_at; read back in a new session | BLOCKED / NOT RUN on this branch | M1/M5 | Not verified on this branch; PR #32 evidence is historical/separate |
| QA-07 | Draw persistence | Read back DRAW state and terminal fields in a new session | NOT RUN | M1/M5 | No execution evidence captured |
| QA-08 | Malformed persisted history | Reject gaps, wrong turn, illegal moves and status/result mismatch | NOT RUN | M1/M5 | No execution evidence captured |
| QA-09 | API write failure and rollback | Force a write failure and prove no partial game/move rows remain | BLOCKED / NOT RUN on this branch | M1 implementation; M5 tests | Persistence/repository implementation absent on this branch |
| QA-10 | Invalid API requests | Missing game, occupied/out-of-range cell, wrong mode/turn/difficulty; verify stored data is unchanged | PARTIAL BASELINE; persistence assertions NOT RUN | M1/M5 | Existing API tests cover several request errors, but no database unchanged assertions were verified |
| QA-11 | PostgreSQL service/API integration | Run persistence acceptance tests against disposable PostgreSQL | NOT RUN; CI job missing | M4 provides DB CI; M1 persistence; M5 tests | tests/test_database_postgres.py is opt-in; workflow currently has no PostgreSQL service/job or test DB env |
| QA-12 | PostgreSQL migration | Test fresh schema and existing-schema backfill for games.public_id | NOT RUN | M4/M1 | No migration execution evidence captured |
| QA-13 | Compose DB smoke | App connects to PostgreSQL; create/move/read across requests or sessions | NOT RUN | M4/M1/M5 | No smoke-run evidence captured |
| QA-14 | Browser E2E | Verify PvP/PvAI and history in browser/deployed environment | NOT RUN | M3/M5 | No browser E2E evidence captured |
| QA-15 | Publish/deploy/live smoke | Verify SHA-tagged image, public HTTPS, and persistence after restart/redeploy | NOT RUN | M4/M3/M1/M5 | No deployment/live-smoke evidence captured |

## Historical PR #32 evidence (not current-branch proof)

- PR #32's separate review worktree reported 183 passed, 11 skipped, 1 warning in the full suite.
- Its repository persistence tests reported 5 passed.
- Its PostgreSQL integration tests reported 11 skipped because TEST_DATABASE_URL was not set.
- These results are evidence about that PR/worktree only. They do not prove the same tests exist or pass on feature/m5-sprint3-qa, and they do not prove PostgreSQL integration passed.
- tests/test_repository_persistence.py was not present on this M5 branch at the time of audit.

## Evidence rules

- Record each run's full commit SHA, command, environment, result, and workflow URL.
- A PASS requires successful execution for the specific environment and scope claimed.
- Overall test-suite success does not independently prove every test category.
- Historical evidence must not be presented as a pass on the current branch.
- PR #32 evidence must not be presented as a result from feature/m5-sprint3-qa.
- SQLite evidence must not be presented as PostgreSQL evidence.
- SKIPPED, NOT RUN and BLOCKED are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Keep this matrix open until the Issue #31 acceptance criteria are met.
