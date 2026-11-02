# M1 Backend Acceptance — `develop` snapshot `e45b077`

**Status:** core backend implementation and baseline CI acceptance **PASS** at the source SHA below. This note is not a production-release sign-off.

## 1. Exact source and validation

| Item | Evidence |
|---|---|
| Source branch | `develop` |
| Exact source SHA | `e45b077fefee9e08136215c366178c2fee4fb81b` |
| Merge commit | PR #44, 2026-11-01 |
| CI workflow | [CaroAI CI #41323745160](https://github.com/emt0147t/caroAI/actions/runs/41323745160) |
| Workflow head | Same exact SHA: `e45b077fefee9e08136215c366178c2fee4fb81b` |
| Python | 3.11.17 |
| PostgreSQL service | 15.19 |
| Workflow conclusion | SUCCESS |

The workflow completed the frontend regression, Python/lint, dedicated PostgreSQL service/API/migration acceptance, Compose persistence-after-restart, and Docker image build jobs. The production publish/Render verification job was **SKIPPED**.

## 2. Backend architecture verified in the source

- `app/api/dependencies.py` injects a request-scoped SQLAlchemy `Session` and builds `GameService(SQLAlchemyGameRepository(db))`.
- `app/db/repository.py` implements `SQLAlchemyGameRepository.transaction()` with `Session.begin()`. SQLAlchemy write failures are converted to `GamePersistenceError` after the transaction context has rolled back.
- `app/services/game_service.py` performs create, read, human move, AI move and history operations through repository unit-of-work transactions. Human and AI move operations load the game for update and persist the move plus game status/result in the same transaction.
- `app/api/routes_games.py` exposes create, get, human-move and AI-move routes; storage failures return HTTP 503 using the generic storage-unavailable detail.
- `app/api/routes_history.py` delegates to `GameService.list_history()` and returns persisted summaries. It does not rely on process-local history.
- The public game ID maps to UUID-shaped `games.public_id`; the BIGINT `games.id` remains the internal database identity.

## 3. Core API contract audit

| Endpoint | Implemented behavior checked against code and `docs/api-contract.md` |
|---|---|
| `POST /api/games` | Creates a persisted game; returns HTTP 201 and a `GameResponse`. |
| `GET /api/games/{game_id}` | Reconstructs state from persisted, ordered moves; unknown public ID returns 404. |
| `POST /api/games/{game_id}/moves` | Validates/applies the current player's move and persists move plus updated game state atomically; invalid game action returns 400. |
| `POST /api/games/{game_id}/ai-move` | Validates AI mode/turn/output and persists the AI move using the same transaction boundary; storage failure returns 503. |
| `GET /api/history` | Returns newest-first game summaries backed by repository/database history, with limit/offset and move count. |

Error format for implemented game/history routes is FastAPI's `{"detail":"..."}`. Readiness is separate: `/health` is liveness; `/ready` checks database connectivity.

## 4. Persistence evidence

The successful exact-SHA CI run includes:

- Dedicated PostgreSQL model/API/migration acceptance: **15 passed, 0 skipped**, 1 warning.
- Fresh-schema and legacy migration acceptance in the dedicated PostgreSQL job.
- API/service acceptance for human and AI moves, terminal state/result, persisted history and session-separated read-back.
- Compose smoke: create a game and move, restart the API container while retaining the disposable PostgreSQL service/volume, then read persisted game/history successfully.
- The generic Python suite separately reports **238 passed, 11 skipped, 1 warning**. Those 11 skips are opt-in PostgreSQL tests in the generic suite; they are not counted as PostgreSQL passes. The dedicated PostgreSQL job has its own zero-skips guard and passed 15/15.

## 5. Transaction rollback evidence

### Baseline test on exact source SHA

At `e45b077`, `tests/postgres_suite.py::test_postgres_api_write_failure_rolls_back` injects a SQLAlchemy failure after `persist_move` stages and flushes the attempted move. It verifies:

1. the API returns HTTP **503**;
2. a fresh SQLAlchemy session sees **zero** persisted moves for that game;
3. the game remains `IN_PROGRESS` and `result` remains `None`.

This test was included in PostgreSQL acceptance run [#41323745160](https://github.com/emt0147t/caroAI/actions/runs/41323745160), which reports **15 passed, 0 skipped**.

### Stronger terminal-state rollback regression in this PR

This PR strengthens that test without changing production transaction code:

1. Persist eight legal moves so X is one move away from five-in-a-row.
2. Inject a `SQLAlchemyError` after the normal repository write has flushed the ninth, winning move and updated the game row's `status`, `result` and `ended_at`.
3. Verify the API returns HTTP 503.
4. Read through a new API request/session and assert the ninth square is empty, `move_count == 8`, status is still `IN_PROGRESS`, and winner is null.
5. Read through a fresh database session and assert exactly eight moves remain, status is `IN_PROGRESS`, result is null, and `ended_at` is null.

The stronger regression is part of this PR and **PASSED** on the exact PR head `d367cf8ed15f03ad2e73e9324ca17437c2ec7ae4`:

- [PR PostgreSQL acceptance job — run #41326199276](https://github.com/emt0147t/caroAI/actions/runs/41326199276/job/124906540503): **15 passed, 0 skipped**, 1 warning.
- The same exact-head push validation [run #41326112186](https://github.com/emt0147t/caroAI/actions/runs/41326112186/job/124906278509) also reports **15 passed, 0 skipped**, 1 warning.
- Workflow run metadata records head SHA `d367cf8ed15f03ad2e73e9324ca17437c2ec7ae4`; the strengthened test implementation was committed as `99c30fba0cee97e83623821527d6c8685c99b2ee`.
- The logs include successful execution of the dedicated PostgreSQL test command and the explicit zero-skipped guard.

The exact-SHA baseline evidence above remains separate. The validation here is specifically for the strengthened test implementation on the replacement PR head; it is not evidence of production deployment.

## 6. PR #35 disposition

[PR #35](https://github.com/emt0147t/caroAI/pull/35) is an old Draft targeting `main`. Its stated implementation uses an in-memory `GameService` history. The accepted implementation on `develop` already registers `GET /api/history` and reads through the SQLAlchemy repository described above. PR #35 must therefore be closed as **superseded**; it must not be merged or used as the release-promotion PR.

This acceptance PR is the replacement handover: it records the already-integrated persistence-backed history contract and adds the stronger rollback regression. It does not copy the stale in-memory implementation from PR #35.

## 7. Acceptance boundary and remaining M1 gates

**PASS at `e45b077`:** backend route/service/repository architecture, the five core API paths, persisted history, new-session persistence evidence, PostgreSQL migration/acceptance job, and baseline transaction rollback.

**Still separate / not claimed by this note:**

- The strengthened terminal-state rollback test requires a successful run on this PR head.
- A local developer's uncommitted Git changes and local branch safety cannot be established by a GitHub CI result.
- Release promotion `develop → main` requires a separate reviewed PR and team sign-offs; this note does not promote `main`.
- Production image publication, Render deployment, public HTTPS smoke, and persistence after a production redeploy were not run by CI #41323745160. Its production job was skipped.

**M1 decision:** backend core acceptance at source SHA `e45b077` is **PASS**. Overall Phase 4 release remains outside this backend acceptance and is not authorized by this document.
