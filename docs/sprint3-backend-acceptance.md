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
- CI Compose smoke on a disposable PostgreSQL database is now implemented: create game, record a move, restart the API container, and verify GET/history persistence. Public/deployed runtime smoke on the published release image remains external.
- Release image publication, deployment, public HTTPS/browser E2E, and team-wide go/no-go.


## Latest CI evidence (2026-10-23)

- Tested source head: `4e63747430ce372772d8903b7c8cd2004dadad94`
- Workflow: https://github.com/emt0147t/caroAI/actions/runs/39912878999
- Frontend checks: PASSED.
- Flake8 and portable pytest: PASSED — 189 passed, 11 skipped, 1 warning. The 11 skips are the opt-in PostgreSQL checks in the generic test job; do not count them as PostgreSQL passes.
- Dedicated PostgreSQL 15 acceptance: PASSED — 15 passed, zero skipped. Coverage includes API/service persistence, human/AI moves, terminal result/time, rollback, migration/backfill and fresh-schema bootstrap.
- Compose runtime smoke: PASSED — built and started the stack with a disposable database, created a game and move, restarted the API container, then verified the board and History API still returned the persisted state.
- Docker image build: PASSED. The image was not published to a registry and the app was not deployed publicly.

Approval/merge of PR #32, release publication, public HTTPS/browser E2E, and the team-wide release decision remain pending.
