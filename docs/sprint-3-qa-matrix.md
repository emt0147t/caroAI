# Sprint 3 QA Matrix — M5

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Baseline SHA on the M5 branch: 2dd55cda274d7112e6d3244a4b457768178e98f8
- Baseline result on that SHA: 178 passed, 11 skipped, 1 warning
- Baseline environment: local Windows; exact Python version was not recorded
- PostgreSQL baseline on the M5 branch: NOT RUN; TEST_DATABASE_URL was not configured
- Current M5 branch source snapshot still uses the in-memory default repository for the service and app/db/repository.py is a placeholder. Persistence acceptance is therefore not implemented/verified on this branch.
- M1 PR #32 head reviewed: e4a91172b518dd16437ca91f72aa594e90da3c7e. Treat all PR #32 evidence as separate from this branch until merged/integrated.
- PR #32 merge-ref CI run #101: FAILED overall: https://github.com/emt0147t/caroAI/actions/runs/39911965014
- Run #101: frontend regression PASSED; PostgreSQL job PASSED with zero skipped tests; test/lint FAILED at Flake8; pytest/Compose in that job and Docker build were SKIPPED.
- Rule: SKIPPED and NOT RUN are not PASS. A source-code audit is not a runtime test.

## Status definitions

- PASSED: the exact test/smoke check ran successfully on the recorded SHA and environment.
- FAILED: the check ran and failed.
- SKIPPED: the runner discovered the check but did not execute it; record the reason.
- NOT RUN: no execution evidence is available.
- BLOCKED: a dependency or missing implementation prevents a meaningful run; do not treat it as PASS.
- PARTIAL: some narrower evidence exists, but the acceptance criterion is not fully covered.

## Evidence matrix

| ID | Area | Acceptance evidence | Status | Owner / dependency | Evidence |
|---|---|---|---|---|---|
| QA-01 | Game rules | Existing regression suite | BASELINE SUITE PASSED; category-specific result not isolated | M5 | M5 baseline SHA; 178 tests passed overall |
| QA-02 | AI | AI integration/regression tests | BASELINE SUITE PASSED; category-specific result not isolated | M2/M5 | M5 baseline run; detailed test names/results not captured |
| QA-03 | API regression | Existing API suite | BASELINE SUITE PASSED; category-specific result not isolated | M1/M5 | M5 baseline SHA; 178 tests passed overall |
| QA-04 | Service persistence across sessions | Create game, apply ordered moves, read via new session | BLOCKED / NOT RUN on M5 branch; PR #32 SQLite evidence exists | M1 implementation; M5 tests | PR #32 test_service_persists_game_and_moves_across_sessions; not on M5 branch |
| QA-05 | API persistence across requests | Create via API, make moves in later requests, GET state | BLOCKED / NOT RUN on M5 branch; PR #32 SQLite evidence exists | M1 implementation; M5 tests | PR #32 test_api_reads_game_created_and_moved_in_previous_requests; not PostgreSQL evidence |
| QA-06 | AI move persistence | Persist/read back AI move across sessions | PARTIAL evidence in PR #32; NOT RUN on M5 branch | M1/M2/M5 | test_ai_move_is_persisted_and_read_back_across_sessions uses a mocked AI engine |
| QA-07 | Terminal win persistence | Persist terminal status/result/winner/ended_at and reload | PARTIAL evidence in PR #32; NOT RUN on M5 branch | M1/M5 | test_terminal_result_and_end_time_persist_across_sessions tests an X horizontal win; no draw case identified |
| QA-08 | Draw persistence | Read back DRAW state/result/ended_at through a new session | NOT RUN | M1/M5 | No draw persistence test identified in PR #32 test_repository_persistence.py |
| QA-09 | Malformed persisted history | Reject non-contiguous move numbers, wrong player turn, illegal moves, status/result mismatch | IMPLEMENTATION CHECKS PRESENT; DIRECT TEST COVERAGE NOT IDENTIFIED | M1/M5 | PR #32 repository _rebuild_state contains validation branches; no dedicated tests for each corruption case identified |
| QA-10 | Service rollback | Inject persistence failure and verify no partial move/game-state changes | PARTIAL evidence in PR #32; NOT RUN on M5 branch | M1/M5 | test_service_transaction_rolls_back_if_move_persistence_fails is SQLite/service-level, not PostgreSQL |
| QA-11 | API write failure/rollback | Trigger write failure through API and assert no partial database records | NOT RUN | M1/M5 | No API-level write-failure/rollback test identified in PR #32 persistence test file |
| QA-12 | Invalid API requests leave storage unchanged | Missing game, occupied/out-of-range cell, wrong mode/turn/difficulty; verify DB rows/state unchanged | PARTIAL API validation tests; persistence invariance NOT RUN | M1/M5 | PR #32 tests/test_games_api.py covers several request errors using InMemoryGameRepository; not database unchanged assertions |
| QA-13 | PostgreSQL model/session constraints | FK, unique move order, coordinate/player checks, rollback | PR #32 PostgreSQL job PASSED; M5 branch NOT RUN | M4 CI; M5 evidence | Run #101 PostgreSQL job passed with zero skips. This is model/session coverage, not proof of service/API PostgreSQL integration unless those tests are included in that job |
| QA-14 | PostgreSQL service/API integration | Run persistence acceptance suite against disposable PostgreSQL | PARTIAL / scope must be confirmed | M1/M4/M5 | PR #32 workflow has a PostgreSQL job, but inspect exact job test command/scope before claiming service/API persistence is covered |
| QA-15 | Migration and backfill | Fresh schema and existing-schema backfill for games.public_id | NOT RUN / not fully verified | M1/M4 | No explicit successful existing-schema migration/backfill evidence recorded |
| QA-16 | Compose DB smoke | App connects to PostgreSQL; create/move/read across requests or sessions | NOT RUN | M1/M4/M5 | Compose validation was skipped in run #101 after lint failure; config validation would not itself prove a DB smoke |
| QA-17 | Browser E2E | Verify PvP/PvAI and history in browser/deployed environment | NOT RUN | M3/M5 | No browser E2E evidence captured |
| QA-18 | Publish/deploy/live smoke | Verify SHA-tagged image, public HTTPS, persistence after restart/redeploy | NOT RUN | M1/M3/M4/M5 | Docker build was skipped in run #101; no live-smoke evidence captured |

## PR #32 code-review findings (not current-M5-branch proof)

The following test names were found in PR #32's separate test file:

- `test_service_persists_game_and_moves_across_sessions`: covers game and ordered moves after a new SQLAlchemy session.
- `test_api_reads_game_created_and_moved_in_previous_requests`: covers create/move/get API flow using SQLite.
- `test_terminal_result_and_end_time_persist_across_sessions`: covers X win, status/result and ended_at; no draw scenario.
- `test_ai_move_is_persisted_and_read_back_across_sessions`: covers AI move persistence with mocked AI.
- `test_service_transaction_rolls_back_if_move_persistence_fails`: covers injected service-level rollback using SQLite.
- `test_history_api_returns_persisted_metadata_and_move_count`: covers history metadata and limit validation.
- `test_create_and_move_routes_do_not_read_state_after_write_commit`: covers route response behavior when a follow-up get_game call is forced to fail.

The repository implementation includes `_rebuild_state` checks for contiguous move numbering, expected player turn, legal moves, and status/result consistency. The reviewed test file did not include a dedicated test for each corrupted-history condition. No explicit draw persistence test or API-level database write-failure/rollback test was identified.

The PostgreSQL test file contains direct model/session tests for ordered moves, unique move numbers, FK, coordinate/player checks, nullable analysis move IDs and transaction rollback on constraint failure. These are not automatically equivalent to GameService/API persistence tests.

## Historical PR #32 CI evidence

- Workflow run #101: https://github.com/emt0147t/caroAI/actions/runs/39911965014
- PostgreSQL job passed and its zero-skips guard passed.
- The overall workflow failed because Flake8 found E302 at `app/schemas/game.py:49` and `tests/test_repository_persistence.py:206`.
- The ordinary test/lint job stopped at lint, so pytest and Compose validation in that job were skipped. Docker build was skipped.
- A prior local PR review reported 5 passed in `tests/test_repository_persistence.py` and 183 passed, 11 skipped in the full suite. Those are historical results from a separate worktree and do not prove current M5 branch behavior.
- Do not report SQLite evidence as PostgreSQL evidence or PR-only evidence as current M5 branch evidence.

## Evidence rules

- Record the exact full commit SHA, command, environment, result, and workflow URL for every run.
- A successful overall test suite does not independently prove every test category.
- SKIPPED, NOT RUN, BLOCKED and IN PROGRESS are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Keep unresolved persistence, draw, malformed-history, API rollback, migration, Compose, browser and live-smoke checks open until corresponding evidence is recorded.
