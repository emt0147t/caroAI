# Database and migration operations

PostgreSQL is the application database. Set DATABASE_URL before starting the backend. Common postgres:// and postgresql:// URLs are normalized to the installed psycopg2-binary driver.

## Apply schema migrations

The container entrypoint runs python -m scripts.migrate_database before starting Uvicorn. To run explicitly from the repository root:

    docker compose up -d db
    docker compose run --rm --no-deps --entrypoint python app -m scripts.migrate_database

Migrations in database/migrations are applied in filename/version order and recorded in schema_migrations. The versioned 000_initial_schema.sql creates the schema for a fresh database and uses CREATE TABLE IF NOT EXISTS to leave existing tables untouched. The versioned 001_games_public_id.sql adds/backfills public_id on legacy games tables, creates a unique index, and enforces NOT NULL. Production migration does not use SQLAlchemy metadata create_all. Future schema changes must use a new versioned SQL file.

The migration command is idempotent for already-recorded versions. Test migration/backfill against a disposable copy before applying it to important data. Never run destructive test fixtures against production/shared databases.

## Readiness

/health is application liveness only. /ready runs SELECT 1 against DATABASE_URL and returns HTTP 503 if the database is unavailable. Compose waits for PostgreSQL health, runs the migration command before Uvicorn, and only marks the API healthy when /ready succeeds.

## PostgreSQL acceptance tests

The dedicated CI job provisions a disposable PostgreSQL 15 database and runs model/session plus FastAPI/GameService/API persistence tests, including ordered moves, terminal state, history, rollback, and migration/backfill. It fails if any acceptance test is skipped.

For manual execution, TEST_DATABASE_URL must point to a disposable PostgreSQL database whose name visibly contains a test token. Set CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database only after verifying the target is disposable. Fixtures create and drop unique per-run schemas and require schema DDL privileges. Database-name checks are guardrails, not proof that a database is safe.

## Evidence boundary

The Compose smoke creates a game, records a move, restarts the API container, and reads the game/history back. This validates the CI-built source image, not a separately published release image or public HTTPS deployment. Release success requires Render to report the exact SHA-tagged image as live and the public /health and /ready checks to pass.
