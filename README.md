# CaroAI

CaroAI is a 15 × 15 Caro game with a FastAPI backend, Python AI package, and static frontend. The Sprint 3 backend branch adds a SQLAlchemy repository that persists games and ordered moves while keeping UUID-shaped public game IDs. The code requires PostgreSQL schema migration for the new `games.public_id` column before it can run against an existing database; M4 owns that migration and the live PostgreSQL/deployment verification.

## Repository layout

```text
app/       FastAPI routes, schemas, game domain, service, database models, AI
ai/        AI package notes
database/  Database implementation notes; migration tooling is not present
docs/      API, domain, AI, database, test, frontend, and DevOps documentation
frontend/  Static frontend files
tests/     Domain, service, API, health, AI, and opt-in PostgreSQL tests
```

## Local setup

Use Python with pip, then from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

The default Uvicorn address is `http://127.0.0.1:8000`; interactive API docs are at `/docs`, and the health endpoint is `/health`.

## Tests

Run all tests or select a suite with pytest:

```powershell
python -m pytest -q
python -m pytest tests/test_game_rules.py -q
python -m pytest tests/test_games_api.py -q
```

PostgreSQL checks in `tests/test_database_postgres.py` are opt-in and create/drop a unique schema. They require a **disposable PostgreSQL test database** with permission to create and drop schemas. Set `TEST_DATABASE_URL` to that database and, only after verifying the target is disposable, set `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`. The fixture also requires the database name to visibly include `test` and rejects names marked `prod` or `live`. Do not point it at production or shared data. No DB tests run without these settings.

The opt-in PostgreSQL suite in `tests/test_database_postgres.py` checks SQLAlchemy models/sessions directly. The new `tests/test_repository_persistence.py` exercises service/API persistence and rollback using SQLite; it is portable regression evidence, not a substitute for running the same integration path against disposable PostgreSQL.

Example PowerShell setup (replace the placeholder with a local disposable test database URL):

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/caroai_test"
$env:CAROAI_TEST_DATABASE_CONFIRMED = "disposable-test-database"
python -m pytest tests/test_database_postgres.py -q
```

The API routes now create a request-scoped SQLAlchemy repository and require `DATABASE_URL`. The versioned migration/backfill for `games.public_id` is still pending under [Issue #30](https://github.com/emt0147t/caroAI/issues/30); do not run this branch against an existing PostgreSQL schema until that migration is applied. See [database design](docs/database-design.md).

## Current boundaries

- The game API supports create, get, human moves, and `POST /api/games/{game_id}/ai-move`. The Sprint 3 repository implementation stores games and ordered moves through SQLAlchemy; PostgreSQL-specific migration/runtime acceptance is still pending.
- Health reports application availability; it does not check PostgreSQL.
- AI move is wired into the game routes. Hint and analysis endpoints are not confirmed as implemented.
- Docker and CI files exist. Their runtime/database smoke behavior is owned by M4 and is not claimed as verified here.

## Documentation

- [API contract](docs/api-contract.md)
- [Game domain](docs/game-domain.md)
- [AI design](docs/ai-design.md)
- [Database design and open decisions](docs/database-design.md)
- [Test plan and current evidence](docs/test-plan.md)
- [Documentation plan](docs/documentation-plan.md)
- [DevOps design](docs/devops-design.md)
- [Frontend design](docs/frontend-design.md)
