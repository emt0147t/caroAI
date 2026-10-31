# CaroAI

CaroAI is a 15 × 15 Caro game with a FastAPI backend, a Python AI engine, a static frontend, and PostgreSQL-backed game persistence. Public game IDs are UUID-shaped strings stored in `games.public_id`; the database retains its internal BIGINT primary key.

## Repository layout

```text
app/        FastAPI routes, schemas, game domain, service, database and AI
database/   Versioned SQL migrations and database operations notes
docs/       API, architecture, QA, release evidence and demo documentation
frontend/   Static frontend files
tests/      Unit, API, persistence, PostgreSQL and Playwright E2E tests
reports/    AI benchmark status and generated evidence
```

## Run locally with Docker Compose (recommended)

Use a local development environment only. From the repository root:

1. Copy the example environment file and replace its sample password with a local-only password:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Build and start PostgreSQL, API and frontend:

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

3. Check application liveness and database readiness:

   ```powershell
   Invoke-RestMethod http://localhost:8000/health
   Invoke-RestMethod http://localhost:8000/ready
   ```

4. Open:
   - Frontend: http://localhost:8080
   - OpenAPI/Swagger UI: http://localhost:8000/docs
   - API liveness: http://localhost:8000/health
   - Database readiness: http://localhost:8000/ready

The API container runs `python -m scripts.migrate_database` before starting Uvicorn. Migrations are versioned SQL files under `database/migrations` and are recorded in `schema_migrations`. Migration 001 backfills UUID-shaped public IDs for legacy game rows, creates the unique index, and enforces NOT NULL. Production schema changes must use a new versioned SQL migration; do not treat SQLAlchemy `create_all` as a production migration mechanism.

To stop the local containers while retaining the PostgreSQL volume:

```powershell
docker compose down
```

Do not add `-v` unless intentionally deleting the local database volume.

## Run the API directly (advanced)

The API uses the configured `DATABASE_URL`. For direct Uvicorn execution, provide a PostgreSQL URL whose schema has been migrated:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
$env:DATABASE_URL = "postgresql+psycopg2://<user>:<password>@localhost:5432/<database>"
python -m scripts.migrate_database
python -m uvicorn app.main:app --reload
```

Use a local disposable/development database, not production credentials or shared data.

## Main API surface

- `POST /api/games` — create a game.
- `GET /api/games/{game_id}` — retrieve authoritative game state.
- `POST /api/games/{game_id}/moves` — submit a human move.
- `POST /api/games/{game_id}/ai-move` — request and persist an AI move.
- `GET /api/history?limit=50&offset=0` — list persisted game History.
- `GET /health` — application liveness; intentionally independent of database availability.
- `GET /ready` — database readiness; executes `SELECT 1` and returns 503 when the configured database is unavailable.

See [API contract](docs/api-contract.md) for request/response details.

## Tests

Run the general suite:

```powershell
python -m pytest -q tests/
```

Run selected suites:

```powershell
python -m pytest tests/test_game_rules.py -q
python -m pytest tests/test_games_api.py -q
python -m pytest tests/test_repository_persistence.py -q
npm ci
npm run test:e2e
```

The Playwright suite expects the real API/frontend stack, normally the Compose stack at `http://127.0.0.1:8080`. Set `CAROAI_BASE_URL` only when intentionally targeting another authorized test environment.

PostgreSQL tests require a **disposable PostgreSQL test database** with permission to create/drop schemas. Set `TEST_DATABASE_URL` and, only after verifying the target is disposable, `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`. The fixture also requires a database name containing a test token and rejects names marked prod/live. Never point it at production or shared data. The dedicated CI PostgreSQL job has an explicit zero-skipped-test guard; general-suite skips are a separate test classification.

## Current QA and release evidence

- [Phase 4 M5 QA matrix](docs/phase4-m5-qa-matrix.md)
- [Phase D evidence register](docs/phase4-m5-d-evidence.md)
- [M5 handover](docs/phase4-m5-handover.md)
- [Seven-minute demo runbook](docs/phase4-m5-e-demo-runbook.md)
- [Issue triage and closure recommendations](docs/phase4-m5-e-issue-triage.md)
- [Release sign-off record](docs/phase4-m5-e-release-signoff.md)
- [Failure triage register](docs/phase4-m5-e-failure-triage.md)
- [M4 release operations](docs/m4-release-operations.md)

The current recorded PR/CI evidence is scoped to the exact SHA and workflows in the QA matrix. PostgreSQL acceptance, Compose API restart persistence, Browser E2E and a Docker image build do **not** prove public deployment or production persistence after redeploy.

## Current release boundaries

- PvP, PvAI, game retrieval, API-backed History and persistence are implemented in the current backend/frontend code.
- Hint and analysis endpoints are not confirmed as implemented; do not present them as available features.
- `/health` is liveness; `/ready` is database readiness.
- The Sprint 3 Linux/Docker AI benchmark and team-approved latency target/SLO remain outstanding. Sprint 2 Windows measurements are historical local measurements, not Phase 4 benchmark acceptance.
- Public HTTPS smoke, production post-redeploy persistence, rollback evidence, approved immutable image identity and formal PR #35 History disposition remain outstanding.
- **Overall Phase 4 release status: BLOCKED / NO-GO.** No production deployment is authorized by this README or by the QA documentation.
