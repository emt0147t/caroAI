# CaroAI — Test Plan and Sprint 2 Evidence

Updated 2026-10-10. This document separates executable current behavior, test coverage, observed results, and integration work blocked by missing implementation or environment. Test code existing in the tree is not counted as passing until executed.

## Test matrix

| Area | Current implementation / coverage | Sprint 2 evidence | Status / owner |
|---|---|---|---|
| Domain rules | Board initialization, legal/occupied moves, four win directions, game end, bounds, and draw cases in `tests/test_game_rules.py` | **PASS** in combined non-API regression command below | M5 QA; domain contract M1 |
| GameService | Create/get/move and per-game isolation; process-local memory only | **PASS** in combined non-API regression command below | M1 implementation; M5 regression |
| Game API | Create, first move, occupied/bounds validation, missing game, win response and post-win rejection | **PASS**: 6 tests passed in isolated Python 3.13 env | M1 API; M5 regression |
| Health | `GET /health` returns `{"status":"ok"}`; no database readiness check | **PASS**: 1 test in isolated Python 3.13 env; no DB readiness assertion | M1 runtime; M5 regression |
| AI unit | Existing move generator, minimax, evaluator, engine unit suites | **PASS** in combined non-API regression command below | M2 owns AI behavior |
| PostgreSQL models | Fresh-session persistence, explicit move-number ordering, FK, unique move number, CHECK constraints, nullable analysis move, rollback | Requires guarded disposable DB; command/result below | M5 DB QA; schema contracts with M1 |
| API/database integration and restart persistence | Not implemented: GameService does not use repository/database | Not run; tests intentionally absent until integration exists | Blocked on M1 repository/transaction/API ID contract |
| AI API integration | No AI endpoints in current routes | Not run | Blocked on M2 AI flow and M1 API contract |
| Docker/Compose DB smoke and CI DB job | Docker and CI configuration files exist; not exercised in this pass | Not run | M4 owns config/readiness/CI environment |

DevOps configuration review (not a test run): `docker-compose.yml` has a PostgreSQL service and app health check but no migration/bootstrap step; this cannot prove database-backed gameplay. `.github/workflows/ci-cd.yml` targets `feature/devops`; its lint command uses `--exit-zero` and its pytest command ends in `|| true`, so those steps do not enforce lint/test failures as CI gates. M4 owns any change to these files and should define an isolated database job and enforcing checks.

## Commands and observed results

### Python compatibility target

CI setup and both Docker stages select Python 3.11. `requirements.txt` does not pin FastAPI or Starlette, and there is no lock or constraints file, so the repository does not define their exact versions. The Windows Python launcher lists 3.13 and 3.14 only; the active shell interpreter is MSYS Python 3.12.12. **No Python 3.11 interpreter was available, so no result below verifies Python 3.11.** No 3.11 venv was created.

Initial all-suite attempt with the system interpreter:

```text
python -m pytest -q
→ NOT RUN: current Python interpreter reports `No module named pytest`.
```

The shell-selected interpreter is Python 3.12.12 from MSYS/UCRT64. Its wheel tags use `mingw_x86_64_ucrt_gnu`, not the standard Windows `win_amd64` tags. Consequently pip selected a source archive for `psycopg2-binary`, which failed because `pg_config` is absent; it also selected a `pydantic-core` source archive, which failed because this platform/SOABI was unsupported and Rust was unavailable. The existing project `.venv` was kept intact apart from installing pytest.

An official Windows Python 3.13.15 interpreter was also available on PATH at `.../Python313/python.exe`. It reports the standard `cp313-cp313-win_amd64` wheel tag. A separate temp venv was created with it; pip resolved FastAPI 0.143.0, Starlette 1.7.0, Pydantic 2.14.0, pytest 9.1.1, and HTTPX 0.28.1, installed as compatible wheels. The repository's Dockerfile and CI use Python 3.11, so 3.13 is a working local Windows test interpreter, while 3.11 remains the CI-aligned target if installed later.

These FastAPI/Starlette versions are observations from that Python 3.13 temp venv only; they are not declared project versions or a prediction of what Python 3.11 CI resolves.

Executed domain/service regression command:

```text
.venv\bin\python.exe -m pytest tests/test_game_rules.py tests/test_game_service.py -q
→ 19 passed in 0.08s
```

Combined domain, service, and AI regression command:

```text
.venv\bin\python.exe -m pytest tests/test_game_rules.py tests/test_game_service.py tests/unit -q
→ 29 passed in 8.49s
```

API/health command (run with the isolated Python 3.13 venv):

```text
<temp-venv>\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_games_api.py tests/test_health.py -q
→ 7 passed, 1 warning in 0.32s; Starlette emitted a deprecation warning because it fell back to `httpx` while recommending `httpx2`.
```

FastAPI's TestClient uses HTTPX. `httpx` was missing from `requirements.txt` and has now been added as an unpinned dependency, consistent with the repository's existing style. The tests pass on the current Starlette stack with a deprecation warning; evaluate its `httpx2` recommendation when the team chooses to pin/update the dependency set. CI installs `requirements.txt` plus pytest, so it now has the dependency used by TestClient.

The five requested groups were subsequently run separately on Windows CPython 3.13.15 (not Python 3.11):

```powershell
$testPython = "$env:TEMP\caroai-m5-api313\Scripts\python.exe"
& $testPython -m pytest -p no:cacheprovider tests/test_game_rules.py -q
& $testPython -m pytest -p no:cacheprovider tests/test_game_service.py -q
& $testPython -m pytest -p no:cacheprovider tests/unit -q
& $testPython -m pytest -p no:cacheprovider tests/test_games_api.py -q
& $testPython -m pytest -p no:cacheprovider tests/test_health.py -q
```

| Command target | Result |
|---|---|
| `tests/test_game_rules.py` | 14 passed, no warnings |
| `tests/test_game_service.py` | 5 passed, no warnings |
| `tests/unit` | 10 passed, no warnings |
| `tests/test_games_api.py` | 6 passed, 1 Starlette deprecation warning |
| `tests/test_health.py` | 1 passed, 1 Starlette deprecation warning |

Across these five Python 3.13.15 suite runs, the final regression total is **36 passed, 0 failed**. The combined API/health invocation recorded **1 Starlette deprecation warning** about the `httpx` fallback and recommendation to use `httpx2`. When API and health were run separately afterward, each invocation emitted that same warning; this is one warning type, not a compatibility failure. No PostgreSQL tests, Docker smoke tests, or CI database job were run, and Python 3.11 remains unverified.

PostgreSQL model checks:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/caroai_test"
$env:CAROAI_TEST_DATABASE_CONFIRMED = "disposable-test-database"
python -m pytest tests/test_database_postgres.py -q
```

This DB command was **not run**: no configured test database was supplied or verified. It requires PostgreSQL with privileges to create/drop schemas. The fixture refuses to perform schema DDL unless the explicit confirmation value is set and the database name contains a `test` token; this is a guardrail, not independent proof that a database is disposable. Confirm the target manually before setting it. The fixture uses a random schema per test and drops only that generated schema; cleanup failures warn without masking an already active test failure.

## Current behavior and acceptance criteria

- **PASS by code review:** DB metadata constraints and runtime boundary are documented against current models.
- **PASS by code review:** in-memory implementation does not claim persistence; API tests do not imply DB integration.
- **PASS:** domain, service, and AI regression suites, 29 tests.
- **PASS:** API and health suites, 7 tests, on Windows CPython 3.13.15 in isolated temp venv.
- **BLOCKED:** PostgreSQL execution; no test database endpoint was provided/verified.
- **BLOCKED:** persistence through GameService/API, restart persistence, repository transaction boundaries: M1 implementation/contract absent.
- **BLOCKED:** AI API tests: AI API flow is not present in this branch; M1/M2 contracts required.
- **NOT RUN:** Docker/Compose smoke or CI database job: M4 environment and acceptance not verified in this pass.

## Ownership and required follow-up

| Dependency | Required decision or implementation | Acceptance evidence |
|---|---|---|
| M1 — persistence | Repository methods, transaction boundary, mapping from API string ID to DB `BIGINT`, service lifecycle | API create/move/read uses DB; data survives a new session and app restart; rollback/error cases verified |
| M1 — schema contract | users/game ownership, statuses/results/ended_at semantics, cascades, unique occupied-cell rule, analysis composite FK/cardinality, migration strategy | Approved schema/migrations and corresponding PostgreSQL constraint tests |
| M2 — AI | AI endpoint integration and behavior/criteria | Contract-backed legal-move/hint/analyze regression with deterministic or bounded assertions |
| M4 — runtime | Compose DB readiness and isolated CI database service/job | Repeatable build/start/health/API-persistence smoke and CI evidence |
| Team/M5 — DB test env | Disposable DB provisioning, isolation, credentials, cleanup privileges | Run PostgreSQL suite in isolated disposable DB; retain test output |

No API persistence, migration, AI API, or Docker DB integration should be described as complete until the evidence above exists.
