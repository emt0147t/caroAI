# Sprint 3 QA Matrix — M5

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Baseline SHA on the M5 branch: 2dd55cda274d7112e6d3244a4b457768178e98f8
- Baseline result on that SHA: 178 passed, 11 skipped, 1 warning
- Baseline environment: local Windows; exact Python version not recorded
- PostgreSQL baseline on the M5 branch: NOT RUN; TEST_DATABASE_URL was not configured
- Current M5 source snapshot still uses an in-memory GameService and app/db/repository.py is a placeholder. Do not treat persistence acceptance as implemented on this branch.
- M1 PR #32 is open and not merged at the time of this audit: https://github.com/emt0147t/caroAI/pull/32
- PR #32 head at the time of audit: e4a91172b518dd16437ca91f72aa594e90da3c7e
- PR #32 merge-ref CI run #101: FAILED overall: https://github.com/emt0147t/caroAI/actions/runs/39911965014
- Run #101 job results: frontend regression PASSED; PostgreSQL service/API/migration acceptance job PASSED with zero skipped tests; test/lint job FAILED at Flake8; Docker build was SKIPPED because a required job failed.
- Flake8 failures in run #101: app/schemas/game.py:49: E302; tests/test_repository_persistence.py:206: E302. Pytest and Compose validation in that job were skipped after Flake8 failed.
- PR #32 description reports an earlier CI run #85 successful at a different head; that result is not a pass for the current merge-ref/run #101.
- PR #32's SQLite persistence test evidence and the M5 baseline are separate evidence sets.
- CI on the M5 branch itself has frontend, test/lint and Docker build jobs, but no dedicated PostgreSQL service/job. The PostgreSQL job above is from the PR #32 merge-ref workflow.
- Rule: SKIPPED and NOT RUN are not PASS. A source-code audit is not a runtime test.

## Status definitions

- PASSED: the exact test/smoke check ran successfully on the recorded SHA and environment.
- FAILED: the check ran and failed.
- SKIPPED: the runner discovered the check but did not execute it; record the reason.
- NOT RUN: no execution evidence is available.
- BLOCKED: a dependency or missing implementation prevents a meaningful run; do not treat this as PASS.
- IN PROGRESS: a workflow was observed running; no success claim until it finishes.

## Evidence matrix

| ID | Area | Acceptance evidence | Status | Owner / dependency | Evidence |
|---|---|---|---|---|---|
| QA-01 | Game rules | Existing regression suite | BASELINE SUITE PASSED; category-specific result not isolated | M5 | M5 baseline SHA; 178 tests passed overall |
| QA-02 | AI | AI integration/regression tests | BASELINE SUITE PASSED; category-specific result not isolated | M2/M5 | M5 baseline run; detailed test names/results not captured |
| QA-03 | API regression | Existing API suite | BASELINE SUITE PASSED; category-specific result not isolated | M1/M5 | M5 baseline SHA; 178 tests passed overall |
| QA-04 | Service/API persistence | Create game, make moves, commit, then read through a new session/service/API | BLOCKED / NOT RUN on M5 branch; SQLite evidence exists on PR #32 | M1 implementation; M5 tests | PR #32 adds service/API SQLite persistence tests, but its changes are not on this M5 branch and the PR is still open |
| QA-05 | AI move persistence | Persist and read back an AI move | BLOCKED / NOT RUN on M5 branch; SQLite evidence exists on PR #32 | M1/M2/M5 | PR #32 test mocks the AI engine; not PostgreSQL evidence |
| QA-06 | Terminal win persistence | Persist status, winner/result and ended_at; read back in a new session | BLOCKED / NOT RUN on M5 branch; SQLite evidence exists on PR #32 | M1/M5 | PR #32 includes an X-win persistence test; draw persistence remains unverified |
| QA-07 | Draw persistence | Read back DRAW state and terminal fields in a new session | NOT RUN | M1/M5 | No execution evidence captured |
| QA-08 | Malformed persisted history | Reject gaps, wrong turn, illegal moves and status/result mismatch | NOT RUN | M1/M5 | PR #32 describes validation behavior, but a passing test for each malformed-history case has not been verified in the available evidence |
| QA-09 | API write failure and rollback | Force a write failure and prove no partial game/move rows remain | PARTIAL: service-level SQLite rollback test in PR #32; API write-failure/rollback not verified | M1 implementation; M5 tests | PR #32 has a service rollback test; do not claim API-level failure/rollback is proven |
| QA-10 | Invalid API requests | Missing game, occupied/out-of-range cell, wrong mode/turn/difficulty; verify stored data is unchanged | PARTIAL BASELINE; persistence assertions NOT RUN on M5 branch | M1/M5 | Existing API tests cover several request errors, but no database-unchanged assertions were verified on this branch |
| QA-11 | PostgreSQL service/API integration | Run service/API persistence acceptance tests against disposable PostgreSQL | PR #32 merge-ref PostgreSQL job PASSED; final PR checks NOT GREEN | M4 provides DB CI; M1 persistence; M5 tests | Run #101 PostgreSQL job passed and zero-skips guard passed; overall workflow failed at Flake8, so build was skipped |
| QA-12 | PostgreSQL migration | Test fresh schema and existing-schema backfill for games.public_id | PARTIAL / NOT FULLY VERIFIED | M4/M1 | Run #101 job is named migration acceptance, but no separate deployed/existing-schema migration evidence is recorded here; verify test scope before closing |
| QA-13 | Compose DB smoke | App connects to PostgreSQL; create/move/read across requests or sessions | NOT RUN | M4/M1/M5 | Compose config validation was skipped in run #101 after lint failed; config validation alone would not prove DB smoke |
| QA-14 | Browser E2E | Verify PvP/PvAI and history in browser/deployed environment | NOT RUN | M3/M5 | No browser E2E evidence captured |
| QA-15 | Publish/deploy/live smoke | Verify SHA-tagged image, public HTTPS, and persistence after restart/redeploy | NOT RUN | M4/M3/M1/M5 | Docker build was skipped in run #101; no deployment/live-smoke evidence captured |

## Historical PR #32 evidence (not current-M5-branch proof)

- PR #32's separate review worktree previously reported 183 passed, 11 skipped, 1 warning in the full suite and 5 passed in tests/test_repository_persistence.py.
- PR #32's PostgreSQL integration suite previously reported 11 skipped because TEST_DATABASE_URL was not set.
- Current PR #32 merge-ref workflow run #101 has a successful PostgreSQL job, but the overall workflow failed because Flake8 found E302 in app/schemas/game.py:49 and tests/test_repository_persistence.py:206. Pytest/Compose in the regular test job and Docker build did not run in that workflow.
- The PostgreSQL job passing on the PR merge ref is meaningful evidence for the exact test scope in that job, but it does not mean all CI checks passed, the PR is merged, the production migration is complete, or deployed persistence has been verified.
- These results do not prove PostgreSQL acceptance on feature/m5-sprint3-qa. tests/test_repository_persistence.py was not present on this M5 branch at the time of audit.

## Evidence rules

- Record each run's full commit SHA, command, environment, result, and workflow URL.
- A PASS requires successful execution for the specific environment and scope claimed.
- Overall test-suite success does not independently prove every test category.
- Historical evidence must not be presented as a pass on the current branch.
- PR #32 evidence must not be presented as a result from feature/m5-sprint3-qa.
- SQLite evidence must not be presented as PostgreSQL evidence.
- SKIPPED, NOT RUN, BLOCKED and IN PROGRESS are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Keep this matrix open until the Issue #31 acceptance criteria are met.
