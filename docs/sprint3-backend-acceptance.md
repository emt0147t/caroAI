# Sprint 3 Backend acceptance checklist

Scope: M1 application persistence and Basic Game History API. This does not replace M2 AI benchmarking, M3 browser E2E, or M4 publication/deployment evidence.

## Implementation
- Production API uses SQLAlchemy-backed GameService; GameRules remains authoritative.
- Public API game IDs remain UUID-shaped games.public_id; internal primary key remains BIGINT games.id.
- Create and move responses use state returned inside the write unit-of-work, avoiding a second state read after commit.
- GET /api/history?limit=50&offset=0 returns newest game summaries with ID, mode, status, result, timestamps, and move count.
- Hint and analysis are outside this implementation.

## Database and test gates
- Versioned migration 001_games_public_id backfills existing rows and enforces unique/non-null public IDs.
- Docker startup applies migration before starting Uvicorn.
- Dedicated CI provisions disposable PostgreSQL, exercises service/API flows, and fails on skipped acceptance tests.
- Tests cover legacy-schema backfill, fresh initialization, new-session read-back, terminal results, AI-move persistence, history listing, and rollback.
- Never run destructive integration fixtures against production/shared databases.

## Still requires external evidence
- Human reviewer approval and merge of PR #32.
- Compose/runtime smoke on the exact built image and database.
- Release image publication, deployment, public HTTPS/browser E2E, and team-wide go/no-go.
