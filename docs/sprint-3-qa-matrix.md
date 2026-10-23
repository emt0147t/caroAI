# Sprint 3 QA Matrix — M5

## Historical evidence snapshot (2026-10-23)

- Earlier review-fix snapshot SHA: `cc25a0f5eaf075ed1cee58944114b99e0d43971a` (historical; superseded by later commits).
- Push CI: [run #250](https://github.com/emt0147t/caroAI/actions/runs/39923635191) — all five required validation jobs passed on this exact SHA.
- Pull-request CI: [run #251](https://github.com/emt0147t/caroAI/actions/runs/39923640767) — all five required validation jobs passed on the same SHA; production publish/deploy verification was skipped by design.
- The five successful validation jobs cover Python tests/lint, PostgreSQL service/API/migration acceptance, Compose persistence after API restart, frontend syntax/regression, and Docker image build.
- Detailed counts from the pre-review-cleanup snapshot only: [push #231](https://github.com/emt0147t/caroAI/actions/runs/39921750450) and [pull_request #232](https://github.com/emt0147t/caroAI/actions/runs/39922033030), SHA `affbb23a90a12dd14f006d8ef692ffdead1e682c`: portable suite 216 passed, 11 skipped, 1 warning; dedicated PostgreSQL acceptance 15 passed, zero skipped.
- Historical/pre-sync only: [run #219](https://github.com/emt0147t/caroAI/actions/runs/39920451798) on `b9a87fe0759dfe51074ce71f5e01cfb45f088f36`.

## Current evidence interpretation

- The last previously verified M5 head is `b333273da91bc2e6bceb8be891ec91112681c9e2`; runs #260/#261 passed on that SHA only and do not cover later commits.
- The earlier `cc25a0f5eaf075ed1cee58944114b99e0d43971a` with runs #250/#251 is historical. Counts 216 passed / 11 skipped / 1 warning and PostgreSQL acceptance 15 passed / 0 skipped belong only to `affbb23a90a12dd14f006d8ef692ffdead1e682c`, runs #231/#232. Run #219 on `b9a87fe0759dfe51074ce71f5e01cfb45f088f36` is historical/pre-sync.
- Latest supplied M3 PR #34 evidence: head `4d540c65f4963d154229214dd34e6dec8f679534`; Browser E2E run #32 passed 13/13 Playwright tests and CaroAI CI run #263 succeeded on that SHA. This is **PARTIAL — M3 PR-only evidence; not verified on M5 head; production/live smoke NOT RUN**.

## Run context

- Repository: emt0147t/caroAI
- QA branch: feature/m5-sprint3-qa
- Persistence integration commit: 67a4dae0694e76264a3f2d06b6fca8fa7368d3b5
- Evidence snapshot commit for Run #197: 3de3bc0477eb9a7308d175077e69e6d5d7141598
- Pre-sync CI-verified handover snapshot at Run #219: b9a87fe0759dfe51074ce71f5e01cfb45f088f36
- Integration commit message: merge: integrate develop persistence into M5 QA branch
- CI workflow run #155 (persistence integration commit): https://github.com/emt0147t/caroAI/actions/runs/39914292428
- CI workflow run #171 (QA documentation head before additional persistence tests): https://github.com/emt0147t/caroAI/actions/runs/39914848382
- CI workflow run #181, attempt 2 (persistence test commit): https://github.com/emt0147t/caroAI/actions/runs/39916011771
- CI workflow run #196 (previous QA docs commit): https://github.com/emt0147t/caroAI/actions/runs/39918306942
- CI workflow run #197 (Python suite detail): https://github.com/emt0147t/caroAI/actions/runs/39918816443
- CI workflow run #198 (previous docs snapshot): https://github.com/emt0147t/caroAI/actions/runs/39919251420
- CI workflow run #219 (pre-sync handover snapshot): https://github.com/emt0147t/caroAI/actions/runs/39920451798
- Run #197 head SHA: 3de3bc0477eb9a7308d175077e69e6d5d7141598; overall SUCCESS; all five jobs passed.
- Run #196 head SHA: 44367370ba5b16f7a2dfcc2908b63ebf3087f627; overall SUCCESS; all five jobs passed.
- Run #181 head SHA: eeecfe569cc8b12cf5cc0f275ba4d5ced53a4192; overall SUCCESS; all five jobs passed.
- Run #171 head SHA: b35e8059bb5ecb430214d4176a322385e8ed6688; overall SUCCESS; all five jobs passed.
- CI head SHA: 3de3bc0477eb9a7308d175077e69e6d5d7141598
- Pre-sync CI overall conclusion: SUCCESS (run #219 on b9a87fe; completed 2026-10-23)
- CI jobs all passed in pre-sync run #219: Run tests and lint; PostgreSQL service/API/migration acceptance; Compose API/database persistence after restart; frontend syntax and regression checks; Docker image build.
- Python suite: 194 passed, 11 skipped, 1 warning (run #197: 5.00 seconds).
- Flake8: PASS, 0 issues. Docker Compose config validation: PASS.
- PostgreSQL acceptance job: PASS, including the workflow's zero-skips guard.
- Compose restart smoke: PASS; the disposable Compose stack created/moved a game, restarted the API, read persisted state, and cleaned up.
- PostgreSQL migration/API acceptance: PASS on this exact M5 commit.
- Frontend syntax and regression: PASS.
- Warning: StarletteDeprecationWarning from fastapi.testclient/httpx integration. Not a test failure.
- Historical baseline SHA 2dd55cda274d7112e6d3244a4b457768178e98f8: 178 passed, 11 skipped, 1 warning; retained as historical baseline only.
- PR #32 pre-merge CI runs #131/#139 remain historical PR-head evidence; use run #155 for evidence on the current M5 branch.
- Browser E2E evidence exists on M3 PR #34 at a different SHA and is **not an E2E run on this M5 head**: Browser E2E run #32 passed **13/13 Playwright tests** on PR #34 head `4d540c65f4963d154229214dd34e6dec8f679534`, and CaroAI CI run #263 succeeded on the same SHA. Older run #30 and its push-run result are historical only. These are CI E2E results, not production/live smoke. M5-head Playwright E2E is not verified.
- Public deployment/HTTPS/live smoke and persistence after restart/redeploy in the deployed environment remain NOT RUN. Compose restart is a disposable CI-stack test only.

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
| QA-04 | Service persistence across sessions | Create game, apply ordered moves, read through new SQLAlchemy session | PASSED on M5 commit | M1/M5 | CI run #155 Python suite: 189 passed; see run URL and SHA in Run context |
| QA-05 | API persistence across requests | API create, moves, GET restored state | PASSED on M5 commit | M1/M5 | CI run #155; Python suite and Compose persistence smoke passed |
| QA-06 | AI move persistence | Persist and reload AI move | PASSED in CI acceptance scope; AI engine mocked | M1/M2/M5 | CI run #155; PostgreSQL API acceptance passed; AI engine is mocked in test |
| QA-07 | Terminal win persistence | Persist status/result/winner/end time and read back | PASSED in CI acceptance scope; X win covered | M1/M5 | CI run #155 PostgreSQL API acceptance and Compose persistence smoke passed |
| QA-08 | Draw persistence | Persist/reload DRAW status, result, ended_at and all 225 moves through a new session | PASSED in Python suite | M1/M5 | Dedicated `test_draw_status_and_all_moves_persist_across_sessions`; run #197 Python suite passed and run #198 passed all five jobs |
| QA-09 | Malformed persisted history | Reject non-contiguous move numbers, wrong player turn, illegal occupied cell, status/result mismatch | PASSED in Python suite | M1/M5 | Four dedicated corrupted-history rejection cases in `tests/test_repository_persistence.py`; run #197 suite passed and run #198 passed all five jobs |
| QA-10 | Service rollback | Inject failure during move persistence and assert no partial move/state | PASSED in CI suite scope | M1/M5 | CI run #155 Python suite passed; PostgreSQL write-failure acceptance also passed |
| QA-11 | API database write failure/rollback | Trigger SQLAlchemy write failure via API and assert HTTP error and no partial rows | PASSED on M5 commit | M1/M4/M5 | CI run #155 PostgreSQL API acceptance passed |
| QA-12 | PostgreSQL model/session constraints | FK, move order uniqueness, coordinate/player checks, analysis checks, transaction rollback | PASSED on M5 commit | M4 CI; M5 evidence | CI run #155 PostgreSQL acceptance passed with zero-skips guard |
| QA-13 | PostgreSQL API acceptance | Human moves, terminal X win, AI move, history metadata | PASSED on M5 commit | M1/M4/M5 | CI run #155 PostgreSQL API acceptance passed |
| QA-14 | PostgreSQL migration | Initialize empty DB; backfill existing public IDs; idempotent rerun | PASSED on M5 commit | M1/M4/M5 | CI run #155 PostgreSQL service/API/migration acceptance passed |
| QA-15 | Compose persistence across API restart | Compose stack: create game, move, restart API container, GET state/history | PASSED on M5 commit (CI disposable stack) | M1/M4/M5 | CI run #155 Compose API/database persistence after restart passed |
| QA-16 | Browser E2E | Verify PvP/PvAI and history in browser against Compose/API/frontend | PARTIAL — M3 PR-only evidence; not verified on M5 head; production/live smoke NOT RUN | M3/M5 | PR #34 head `4d540c65f4963d154229214dd34e6dec8f679534`: [Browser E2E run #32](https://github.com/emt0147t/caroAI/actions/runs/39926139293) passed 13/13 Playwright tests; [CaroAI CI run #263](https://github.com/emt0147t/caroAI/actions/runs/39926139313) succeeded on the same SHA; Older run #30 and its push-run result are historical only; the latest supplied M3 evidence is run #32/#263. Neither validates M5-head E2E or production/live smoke |
| QA-17 | Publish/deploy/live smoke | Verify image publication, public HTTPS and persistence after deployment restart | NOT RUN | M1/M3/M4 (M5 records evidence only) | No deployment/live-smoke evidence identified; keep Issue #31 open until owners complete or team explicitly accepts the gap

## Merged M1 implementation test inventory (not M5-branch proof)

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

The repository implementation has `_rebuild_state` checks for contiguous move numbers, expected player turn, legal moves, and status/result consistency. `tests/test_repository_persistence.py` now includes four corrupted-history rejection cases and a draw persistence test that checks all 225 moves, DRAW status/result, ended_at, and reloading through a new database session. These tests passed in the Python suite on run #197.

## CI evidence and limitations

- Earlier review-fix snapshot `cc25a0f5eaf075ed1cee58944114b99e0d43971a`: [push run #250](https://github.com/emt0147t/caroAI/actions/runs/39923635191) and [pull_request run #251](https://github.com/emt0147t/caroAI/actions/runs/39923640767) both passed all five required validation jobs. The publish/deploy verification job in #251 was skipped by design.
- Pre-review-cleanup detailed-count snapshot `affbb23a90a12dd14f006d8ef692ffdead1e682c`: [push run #231](https://github.com/emt0147t/caroAI/actions/runs/39921750450) and [pull_request run #232](https://github.com/emt0147t/caroAI/actions/runs/39922033030); portable suite 216 passed, 11 skipped, 1 warning; PostgreSQL acceptance 15 passed, zero skipped.
- Persistence integration workflow run #155: https://github.com/emt0147t/caroAI/actions/runs/39914292428 — SUCCESS on commit 67a4dae0694e76264a3f2d06b6fca8fa7368d3b5.
- QA documentation workflow run #171: https://github.com/emt0147t/caroAI/actions/runs/39914848382 — SUCCESS on commit b35e8059bb5ecb430214d4176a322385e8ed6688.
- Persistence test workflow run #181, attempt 2: https://github.com/emt0147t/caroAI/actions/runs/39916011771 — SUCCESS on commit eeecfe569cc8b12cf5cc0f275ba4d5ced53a4192; all five jobs passed.
- Workflow run #197: https://github.com/emt0147t/caroAI/actions/runs/39918816443 — SUCCESS on code/test commit 3de3bc0477eb9a7308d175077e69e6d5d7141598; Python suite: 194 passed, 11 skipped, 1 warning in 5.00 seconds.
- Pre-sync workflow run #219: https://github.com/emt0147t/caroAI/actions/runs/39920451798 — SUCCESS on commit b9a87fe0759dfe51074ce71f5e01cfb45f088f36; all five jobs passed. Run #219 is historical/pre-sync evidence only and does not validate the final review-fix head.
- All five jobs passed: Run tests and lint; PostgreSQL service/API/migration acceptance; Compose API/database persistence after restart; frontend syntax and regression checks; Docker image build.
- Python suite: 189 passed, 11 skipped, 1 warning in 4.34 seconds. Flake8 reported 0 issues; Docker Compose config validation passed.
- PostgreSQL acceptance passed with the zero-skips guard. Compose restart smoke passed on a disposable CI stack.
- The Compose smoke is not evidence of public deployment, public HTTPS, or deployed persistence after restart.
- One StarletteDeprecationWarning from fastapi.testclient/httpx remains; it did not fail the run.
- Historical PR #32 runs #131/#139 and run #101 remain pre-merge evidence and must not override current M5 evidence from runs #197/#198.
- Dedicated draw persistence and four corrupted-history cases are included in the Python suite for commit eeecfe569cc8b12cf5cc0f275ba4d5ced53a4192 and remain present at the current commit; the suite passed in runs #181 and #197.
- The generic `python -m pytest -q tests/` job reports 11 skipped on the recorded historical snapshot. `tests/test_database_postgres.py` explicitly skips its integration cases unless `TEST_DATABASE_URL` and `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database` are set. The separate PostgreSQL acceptance job passed with its zero-skips guard; do not conflate the two test invocations.
- Browser E2E and public deployed/live smoke remain NOT RUN.

## Evidence rules

- Record the exact full commit SHA, command, environment, result, and workflow URL for every run.
- Overall test-suite success does not independently prove every test category.
- Merged-develop evidence must not be presented as a result from feature/m5-sprint3-qa until the M5 branch contains the same implementation and the relevant checks are rerun.
- SQLite evidence must not be presented as PostgreSQL evidence.
- SKIPPED, NOT RUN, BLOCKED and PARTIAL are not PASS.
- Do not store credentials, tokens, or production database URLs in this file.
- Dedicated draw persistence and four malformed-history corruption cases are implemented and passed in the Python suite on runs #181 and #197.
- Browser E2E is PARTIAL: M3 PR #34 pull_request run #30 passed 13/13 on SHA `31a000989408d86ff6cdc863913f45d69832ce0a`, while its push run failed; neither run is an E2E result for this M5 head. Public deployment/live smoke and deployed restart/redeploy persistence remain NOT RUN. Compose smoke is limited to a disposable CI environment.
- Earlier review-fix snapshot `cc25a0f5eaf075ed1cee58944114b99e0d43971a`: [push run #250](https://github.com/emt0147t/caroAI/actions/runs/39923635191) and [pull_request run #251](https://github.com/emt0147t/caroAI/actions/runs/39923640767) passed all five required validation jobs on that exact SHA. Pre-review-cleanup runs #231/#232 on `affbb23a90a12dd14f006d8ef692ffdead1e682c` hold the detailed test counts above. Run #219 on `b9a87fe0759dfe51074ce71f5e01cfb45f088f36` is historical/pre-sync only. Persistence integration originally landed at `67a4dae0694e76264a3f2d06b6fca8fa7368d3b5` in run #155.
