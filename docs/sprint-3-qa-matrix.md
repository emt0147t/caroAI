# Sprint 3 QA Matrix — M5

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Baseline SHA on M5 branch: 2dd55cda274d7112e6d3244a4b457768178e98f8
- Baseline result on that SHA: 178 passed, 11 skipped, 1 warning
- Baseline environment: local Windows; exact Python version not recorded
- PostgreSQL test run on the M5 baseline: NOT RUN; TEST_DATABASE_URL was not configured
- Current M5 branch does not yet contain M1's SQLAlchemy persistence implementation; the matrix records PR #32 evidence separately.
- M1 PR #32 head at latest inspection: 50435a02bca65e08cace8ad3d0a539981bc4c0d8; PR remains open and unmerged. Evidence below is PR-only until the implementation is integrated into the M5 branch.
- Earlier workflow run #101 failed at Flake8 E302. It was superseded by run #131 at the then-current PR head 4e63747430ce372772d8903b7c8cd2004dadad94.
- Run #131: https://github.com/emt0147t/caroAI/actions/runs/39912882803 — overall SUCCESS for SHA 4e63747430ce372772d8903b7c8cd2004dadad94. All five jobs passed: frontend, test/lint, PostgreSQL acceptance with zero-skips guard, Compose persistence after API restart, and Docker image build.
- PR #32 has since advanced to SHA 50435a02bca65e08cace8ad3d0a539981bc4c0d8. Its new workflow run #139 is IN PROGRESS: https://github.com/emt0147t/caroAI/actions/runs/39913192666. Do not infer a result until that run completes.
- The Compose job explicitly built and started a disposable stack, created/moved a game, restarted the API, read persisted state, and cleaned up resources.
- Important: run #131 is evidence for PR #32's head, not for feature/m5-sprint3-qa, because M1 persistence has not been integrated into the M5 branch.

## Status definitions

- PASSED: the exact test/check ran successfully on the recorded commit and environment.
- FAILED: the check ran and failed.
- SKIPPED: the runner discovered the check but did not execute it; record the reason.
- NOT RUN: no execution evidence is available.
- BLOCKED: a dependency or missing implementation prevents a meaningful run.
- PARTIAL: narrower evidence exists but does not meet the entire acceptance criterion.
- PR-ONLY: evidence belongs to PR #32 and is not proof for the M5 branch.

## Evidence matrix

| ID | Area | Acceptance evidence | Status | Owner / dependency | Evidence |
|---|---|---|---|---|---|
| QA-01 | Game rules | Existing regression suite | M5 BASELINE SUITE PASSED; category-specific result not isolated | M5 | Baseline SHA; 178 passed overall |
| QA-02 | AI | AI integration/regression tests | M5 BASELINE SUITE PASSED; category-specific result not isolated | M2/M5 | Baseline SHA; detailed test names/results not captured |
| QA-03 | API regression | Existing API suite | M5 BASELINE SUITE PASSED; category-specific result not isolated | M1/M5 | Baseline SHA; 178 passed overall |
| QA-04 | Service persistence across sessions | Create game, apply ordered moves, read through new SQLAlchemy session | PR-ONLY: test exists; prior local review passed; NOT RUN on M5 branch | M1/M5 | PR #32 test_service_persists_game_and_moves_across_sessions |
| QA-05 | API persistence across requests | API create, two moves, GET restored state | PR-ONLY: test exists; prior local review passed; NOT RUN on M5 branch | M1/M5 | PR #32 test_api_reads_game_created_and_moved_in_previous_requests, using SQLite |
| QA-06 | AI move persistence | Persist and reload AI move | PR-ONLY: covered with mocked AI; NOT RUN on M5 branch | M1/M2/M5 | test_ai_move_is_persisted_and_read_back_across_sessions; PostgreSQL suite also has API AI move with mocked engine |
| QA-07 | Terminal win persistence | Persist status/result/winner/end time and read back | PR-ONLY: X win covered; NOT RUN on M5 branch | M1/M5 | test_terminal_result_and_end_time_persist_across_sessions; PostgreSQL API acceptance test checks X win and ended_at in history |
| QA-08 | Draw persistence | Persist/reload DRAW status, result and ended_at | NOT RUN; no dedicated draw test identified | M1/M5 | No draw persistence case identified in the reviewed PR #32 tests |
| QA-09 | Malformed persisted history | Reject non-contiguous move numbers, wrong turn, illegal moves, status/result mismatch | IMPLEMENTATION VALIDATION PRESENT; DEDICATED CORRUPTION TESTS NOT IDENTIFIED | M1/M5 | PR #32 _rebuild_state checks these invariants; no dedicated test per corruption case found in reviewed test files |
| QA-10 | Service rollback | Inject failure during move persistence and assert no partial move/state | PR-ONLY: SQLite service-level test exists; NOT RUN on M5 branch | M1/M5 | test_service_transaction_rolls_back_if_move_persistence_fails |
| QA-11 | API database write failure/rollback | Trigger SQLAlchemy write failure via API and assert HTTP error and no partial rows | PR-ONLY: PostgreSQL acceptance test exists; run #101 PostgreSQL job passed; NOT RUN on M5 branch | M1/M4/M5 | tests/postgres_suite.py::test_postgres_api_write_failure_rolls_back expects HTTP 503 and verifies no move row/state change |
| QA-12 | PostgreSQL model/session constraints | FK, move order uniqueness, coordinate/player checks, analysis checks, transaction rollback | PR-ONLY: PostgreSQL job PASSED in run #131; M5 branch NOT RUN | M4 CI; M5 evidence | Run #131 executed tests/test_database_postgres.py and tests/postgres_suite.py; zero-skips guard passed |
| QA-13 | PostgreSQL API acceptance | Human moves, terminal X win, AI move, history metadata | PR-ONLY: PostgreSQL job PASSED in run #131; M5 branch NOT RUN | M1/M4/M5 | tests/postgres_suite.py::test_postgres_api_human_ai_terminal_state_and_history |
| QA-14 | PostgreSQL migration | Initialize empty DB; backfill existing public IDs; idempotent rerun | PR-ONLY: migration tests included in PostgreSQL job that PASSED in run #131; M5 branch NOT RUN | M1/M4/M5 | test_migration_initializes_an_empty_database; test_migration_backfills_existing_public_ids_and_is_idempotent |
| QA-15 | Compose persistence across API restart | Compose stack: create game, move, restart API container, GET state/history | PR-ONLY: PASSED in run #131; M5 branch NOT RUN | M1/M4/M5 | Workflow file inspected on PR head contains a compose-smoke job, but run #101 job list did not include that job; do not mark it passed |
| QA-16 | Browser E2E | Verify PvP/PvAI and history in browser/deployed environment | NOT RUN | M3/M5 | No browser E2E result identified |
| QA-17 | Publish/deploy/live smoke | Verify image publication, public HTTPS and persistence after deployment restart | NOT RUN | M1/M3/M4/M5 | No deployment/live-smoke evidence identified |

## PR #32 test inventory reviewed (not M5-branch proof)

SQLite/service/API tests in tests/test_repository_persistence.py include:
- test_service_persists_game_and_moves_across_sessions
- test_api_reads_game_created_and_moved_in_previous_requests
- test_terminal_result_and_end_time_persist_across_sessions
- test_ai_move_is_persisted_and_read_back_across_sessions (AI engine mocked)
- test_service_transaction_rolls_back_if_move_persistence_fails
- test_history_api_returns_persisted_metadata_and_move_count
- test_create_and_move_routes_do_not_read_state_after_write_commit

The PostgreSQL acceptance suite in tests/postgres_suite.py includes:
- test_postgres_api_human_ai_terminal_state_and_history
- test_postgres_api_write_failure_rolls_back
- test_migration_backfills_existing_public_ids_and_is_idempotent
- test_migration_initializes_an_empty_database

The PostgreSQL model/session suite in tests/test_database_postgres.py includes checks for ordered move persistence across sessions, unique move numbers, foreign keys, coordinate/player/move-number constraints, nullable analysis move ID, analysis coordinate constraints, and rollback after a constraint failure.

The reviewed repository implementation has _rebuild_state checks for contiguous move numbers, expected player turn, legal moves, and status/result consistency. Dedicated tests that deliberately corrupt persisted history to exercise each validation branch were not identified. No dedicated draw persistence test was identified.

## CI evidence and limitations

- Workflow run #101: https://github.com/emt0147t/caroAI/actions/runs/39911965014
- Frontend job: PASSED.
- PostgreSQL service/API/migration acceptance job: PASSED; the zero-skipped guard passed.
- Ordinary test/lint job: FAILED at Flake8 E302 in app/schemas/game.py:49 and tests/test_repository_persistence.py:206. Pytest and Compose config validation in that job were skipped.
- Docker build: SKIPPED because required jobs did not all pass.
- The PR workflow file currently defines a Compose smoke job, but the run #101 job list returned by GitHub did not include it. Its result is therefore not verified for run #101.
- A prior local review reported 5 passed in tests/test_repository_persistence.py and 183 passed, 11 skipped in the full suite. These are historical PR worktree results, not current M5 branch results.
- A successful PostgreSQL job does not mean the overall workflow passed, nor does it prove browser E2E, published image, public HTTPS or live deployed restart persistence.

## Evidence rules

- Record the exact full commit SHA, command, environment, result, and workflow URL for every run.
- Overall test-suite success does not independently prove every test category.
- PR-only evidence must not be presented as a result from feature/m5-sprint3-qa.
- SQLite evidence must not be presented as PostgreSQL evidence.
- SKIPPED, NOT RUN, BLOCKED and PARTIAL are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Keep draw and malformed-history corruption tests, current-branch integration, browser E2E and live deployment smoke open until the corresponding evidence is recorded. Compose restart smoke has PR-only passing evidence in run #131.
