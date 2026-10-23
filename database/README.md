# Database and migration operations

PostgreSQL is the application database. Set DATABASE_URL before starting the backend.

## Apply schema migration

The Docker entrypoint runs:

```bash
python -m scripts.migrate_database
```

- An empty database is initialized from current SQLAlchemy metadata; version 001_games_public_id is then recorded.
- If a legacy games table already exists, the migration runner does not use create_all to alter that table. It applies the versioned SQL migration to add public_id, backfill UUID values for existing rows, create the unique index, and enforce NOT NULL before recording the version.
- The migration command is idempotent for the recorded version. Future schema changes must use a new migration version.

The first migration assumes that an existing database already has the project’s legacy games table and internal primary key. Test migration/backfill against a disposable copy before applying it to important data. Never run destructive test fixtures against production/shared databases.

## PostgreSQL acceptance tests

The dedicated CI job provisions a disposable PostgreSQL 15 database and runs model tests plus tests through the actual FastAPI/GameService routes, including ordered move persistence, terminal result/time, history listing, rollback, and migration/backfill. The workflow fails if any acceptance test is skipped.

For manual execution, TEST_DATABASE_URL must point to a disposable PostgreSQL database whose name contains a test token. Set CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database only after verifying the target is disposable. Fixtures create and drop unique per-run schemas and require schema DDL privileges. Database-name checks are guardrails, not proof that a database is safe.
