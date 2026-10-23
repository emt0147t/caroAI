# Sprint 3 QA Matrix — M5

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Baseline SHA: 2dd55cda274d7112e6d3244a4b457768178e98f8
- Baseline result: 178 passed, 11 skipped, 1 warning
- Baseline environment: local Windows; exact Python version not recorded
- PostgreSQL baseline: NOT RUN; TEST_DATABASE_URL was not configured
- Important: historical results are not proof of a pass on the current branch.
- Rule: SKIPPED and NOT RUN are not PASS.

## Evidence matrix

| ID | Area | Acceptance evidence | Status | Owner / dependency | Evidence |
|---|---|---|---|---|---|
| QA-01 | Game rules | Existing regression suite | BASELINE SUITE PASSED; category-specific result not isolated | M5 | Historical baseline SHA above; 178 tests passed overall |
| QA-02 | AI | AI integration/regression tests | BASELINE SUITE PASSED; category-specific result not isolated | M2/M5 | Historical baseline; detailed test names/results not captured here |
| QA-03 | API regression | Existing API suite | BASELINE SUITE PASSED; category-specific result not isolated | M1/M5 | Historical baseline; 178 tests passed overall |
| QA-04 | Service/API persistence on SQLite | Create game, make moves, read back through a new session/API | PR EVIDENCE ONLY; not verified on this branch | M1/M5 | PR #32: tests/test_repository_persistence.py; historical PR test run |
| QA-05 | AI move persistence | Persist and read back an AI move | PR EVIDENCE ONLY; AI was mocked | M1/M2/M5 | PR #32 persistence test; not PostgreSQL evidence |
| QA-06 | Terminal win persistence | Persist status, result, winner, ended_at | PR EVIDENCE ONLY; not verified on this branch | M1/M5 | PR #32 persistence test |
| QA-07 | Draw persistence | Read back DRAW state and terminal fields in a new session | NOT RUN / test not identified | M1/M5 | Pending |
| QA-08 | Malformed persisted history | Reject gaps, wrong turn, illegal moves, and status/result mismatch | NOT RUN / test not identified | M1/M5 | Pending |
| QA-09 | API write failure | Return contract-defined error and leave no partial records | NOT RUN / end-to-end behavior not verified | M1/M5 | Pending |
| QA-10 | Invalid API requests | Missing game, occupied/out-of-range cell, wrong mode/turn/difficulty; verify DB unchanged | NOT RUN / persistence assertions pending | M1/M5 | Pending |
| QA-11 | PostgreSQL service/API integration | Run persistence acceptance tests against disposable PostgreSQL | NOT RUN | M4 provides DB CI; M5 tests; M1 persistence | Issue #30 / Issue #23 |
| QA-12 | PostgreSQL migration | Test fresh schema and existing-schema backfill for games.public_id | NOT RUN | M4/M1 | Issue #30 |
| QA-13 | Compose DB smoke | App connects to PostgreSQL; create/move/read across requests or sessions | NOT RUN | M4/M1/M5 | Pending |
| QA-14 | Browser E2E | Verify PvP/PvAI and history in browser/deployed environment | NOT RUN | M3/M5 | Pending |
| QA-15 | Publish/deploy/live smoke | Verify SHA-tagged image, public HTTPS, and persistence after restart/redeploy | NOT RUN | M4/M3/M1/M5 | Issue #30 |

## Evidence rules

- Record each run's full commit SHA, command, environment, result, and workflow URL.
- A PASS requires successful execution for the specific environment and scope claimed.
- Overall test-suite success does not independently prove every test category.
- Historical evidence must not be presented as a pass on the current branch.
- PR #32 evidence must not be presented as a result from feature/m5-sprint3-qa.
- SQLite evidence must not be presented as PostgreSQL evidence.
- SKIPPED and NOT RUN are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Keep this matrix open until the Issue #31 acceptance criteria are met.
