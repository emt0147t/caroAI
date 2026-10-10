# CaroAI

CaroAI is a 15 × 15 Caro game with a FastAPI backend, an in-memory game service, a Python AI package, and a static frontend. The repository also contains a PostgreSQL/SQLAlchemy schema foundation. **Game creation and moves currently live only in process memory**; PostgreSQL persistence, migrations, and database-backed gameplay are not integrated.

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
python -m pip install -r requirements.txt
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

Example PowerShell setup (replace the placeholder with a local disposable test database URL):

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/caroai_test"
$env:CAROAI_TEST_DATABASE_CONFIRMED = "disposable-test-database"
python -m pytest tests/test_database_postgres.py -q
```

`DATABASE_URL` is read by the application database helper if/when database access is invoked. It is not needed to start the current in-memory API. The repository has no migration tool or schema migration command yet. See [database design](docs/database-design.md) for current tables and unresolved decisions.

## Current boundaries

- The game API supports create, get, and human moves in the current implementation.
- Health reports application availability; it does not check PostgreSQL.
- AI code and unit tests exist, but an API AI move/hint/analyze flow is not wired into the game routes.
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
