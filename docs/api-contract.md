# CaroAI API Contract and Endpoint Status

This document describes the implemented routes and distinguishes them from proposed interfaces. The game routes use a request-scoped SQLAlchemy repository; PostgreSQL stores `games` and ordered `moves`, and the domain state is reconstructed from persisted move history. The versioned migrations are implemented under `database/migrations` and run through `python -m scripts.migrate_database`; the dedicated PostgreSQL CI job validates both fresh-schema initialization and legacy `games.public_id` backfill. Passing CI is not evidence that the public production service has been deployed or smoke-tested.

## Health and readiness

### `GET /health`

Returns HTTP `200` with:

```json
{"status": "ok"}
```

This is an application liveness response only; it deliberately does not check PostgreSQL.

### `GET /ready`

Executes `SELECT 1` against the configured database. When the query succeeds, returns HTTP `200`:

```json
{"status": "ready", "database": "ok"}
```

If the database URL is missing or the database cannot be queried, returns HTTP `503`:

```json
{"detail": "Database is not ready"}
```

Readiness confirms basic database connectivity. It does not by itself prove API persistence, migration correctness, public deployment health, or persistence after a restart.

## Implemented game endpoints

### `POST /api/games`

Creates a persisted game record through the configured repository. The request accepts `mode` from `HUMAN_VS_HUMAN` or `HUMAN_VS_AI`; if omitted, the schema default is `HUMAN_VS_HUMAN`. The returned `id` is the UUID-shaped `games.public_id`; `games.id` remains an internal BIGINT identity.

Returns HTTP `201` and a `GameResponse` containing `id` (string), `mode`, `status`, `current_player`, `move_count`, `winner`, and a 15 × 15 `board`. A new game starts `IN_PROGRESS`, with X to move, zero moves, and no winner.

### `GET /api/games/{game_id}`

Rebuilds and returns the game state from persisted, move-number-ordered history with HTTP `200`. An unknown public ID returns HTTP `404`:

```json
{"detail": "Game 'does-not-exist' not found"}
```

The detail embeds the requested ID, as produced by `GameNotFoundError` in the current implementation.

The endpoint rebuilds the board and current game state from the ordered persisted moves. A missing public ID returns HTTP `404`.

### `POST /api/games/{game_id}/moves`

Accepts integer `row` and `col`, each validated in the inclusive range `0..14`. The server chooses the player from `current_player`; the request does not accept a player field.

Returns HTTP `200` with `move` (`row`, `col`, `player`, `move_number`) and the updated `game` response. An unknown game returns `404`. A rule violation (occupied cell or finished game) returns `400` with FastAPI's `detail` string. Request validation errors, including out-of-range coordinates, return `422`.

The game rules alternate X/O after a non-terminal move. A run of five or more contiguous marks in any of four directions ends the game with `X_WON` or `O_WON`; filling the final cell without a win ends it with `DRAW`. No further move is accepted after a terminal status.

## Implemented AI move

### `POST /api/games/{game_id}/ai-move`

This endpoint is implemented in the current Backend. It is available only for games created with `mode: "HUMAN_VS_AI"`, and only when it is the AI (O) turn. The request schema defaults `difficulty` to `"medium"` when omitted.

Request:

```json
{"difficulty":"medium"}
```

Allowed values are `easy`, `medium`, and `hard`. Unsupported values or invalid request data return HTTP `422`.

Successful response: HTTP `200`, using the same `MakeMoveResponse` schema as a human move. Schema excerpt (the actual `game.board` field is a 15 × 15 array and is omitted here for readability):

```json
{
  "move": {"row": 6, "col": 8, "player": "O", "move_number": 2},
  "game": {
    "id": "game-id",
    "mode": "HUMAN_VS_AI",
    "status": "IN_PROGRESS",
    "current_player": "X",
    "move_count": 2,
    "winner": null
  }
}
```

The coordinates are illustrative; the actual move is selected by the AI. Unknown game IDs return HTTP `404`. Requests that cannot be applied (wrong game mode, not the AI turn, or illegal AI output) return HTTP `400`. Request-schema validation errors, including an unsupported difficulty, return HTTP `422`. Errors use FastAPI's `{"detail":"..."}` shape.

The AI endpoint computes and validates a move from a Backend-owned state snapshot, then persists the move and updated status/result in the same repository transaction. The versioned PostgreSQL migration and dedicated PostgreSQL acceptance suite are implemented and tested in CI. Public production deployment and live-database smoke evidence remain separate release gates.

## Game History API

### `GET /api/history`

Returns persisted game summaries, newest first, for the MVP History UI. Optional query parameters are `limit` (default 50, range 1–100) and `offset` (default 0, non-negative). The response contains `items`, `limit` and `offset`. Each item contains the public ID, mode, status, result, `started_at`, `ended_at` and `move_count`. Use `GET /api/games/{game_id}` to retrieve the board. Query validation errors return HTTP `422`; storage errors return HTTP `503`.

This endpoint does not imply user ownership/authentication, replay or analysis support.

## Planned interfaces — not implemented

| Interface | Status |
|---|---|
| `POST /api/games/{game_id}/hint` | Not implemented in current routes |
| `POST /api/games/{game_id}/analysis` | Not implemented in current routes |

Do not treat these paths as callable APIs until their routes and schemas are implemented and verified.

## Error response format

Implemented error responses use FastAPI's standard JSON shape:

```json
{"detail": "Human-readable error message"}
```

The implemented game routes use `400` for invalid game actions, `404` for missing games, and `422` for request validation. Game/history storage transaction errors return `503` with a generic storage-unavailable detail. The readiness route also returns `503` if it cannot query the database. The exact `GET /api/games/{game_id}` `404` detail includes the requested game ID as shown above.

## Runtime boundary

Implemented game/history routes → `GameService` → SQLAlchemy repository/unit-of-work → `games` and ordered `moves`; Backend `GameRules` remains authoritative. The API-facing `id` maps to `games.public_id` and BIGINT `games.id` is internal. The versioned migration and disposable-PostgreSQL acceptance checks exist in the repository and are exercised by CI. Production/Render deployment, public HTTPS smoke, and persistence after a production restart/redeploy are still release gates and must not be inferred from CI success. Hint and analysis routes are not implemented.

See [game-domain.md](game-domain.md) for the implemented state/rules, [database-design.md](database-design.md) for the schema foundation and open decisions, and [test-plan.md](test-plan.md) for test strategy and the current evidence boundary.
