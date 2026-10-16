# CaroAI API Contract and Endpoint Status

This document distinguishes routes currently implemented in this branch from proposed interface designs. It is not evidence that planned API or database integration is available. The game API currently delegates to an in-memory `GameService`; game state does not survive process restart.

## Implemented endpoints

### `GET /health`

Returns HTTP `200` with:

```json
{"status": "ok"}
```

This is an application health response only; it does not check PostgreSQL.

### `POST /api/games`

Creates an in-memory game. The request accepts a `mode` from `HUMAN_VS_HUMAN` or `HUMAN_VS_AI`; if omitted, the schema default is `HUMAN_VS_HUMAN`.

Returns HTTP `201` and a `GameResponse` containing `id` (string), `mode`, `status`, `current_player`, `move_count`, `winner`, and a 15 × 15 `board`. A new game starts `IN_PROGRESS`, with X to move, zero moves, and no winner.

### `GET /api/games/{game_id}`

Returns the current process-local `GameResponse` with HTTP `200`. An unknown ID returns HTTP `404`:

```json
{"detail": "Game 'does-not-exist' not found"}
```

The detail embeds the requested ID, as produced by `GameNotFoundError` in the current implementation.

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

The AI endpoint changes the in-memory `GameState` only. It does **not** demonstrate PostgreSQL persistence.

## Planned interfaces — not confirmed as implemented

| Interface | Status |
|---|---|
| `POST /api/games/{game_id}/hint` | Not confirmed as implemented in current routes |
| `POST /api/games/{game_id}/analysis` | Not confirmed as implemented in current routes |
| `GET /api/history` | Not confirmed as implemented; persistence contract remains open |

Do not treat these paths or earlier examples as callable APIs until their owners verify the routes and schemas.

## Error response format

Implemented error responses use FastAPI's standard JSON shape:

```json
{"detail": "Human-readable error message"}
```

The implemented game routes use `400` for invalid game actions, `404` for missing games, and `422` for request validation. The exact `404` detail includes the requested game ID as shown above.

## Runtime boundary

Implemented routes → `GameService` → domain rules/state. `GameService` stores state in a process-local dictionary. The SQLAlchemy models/session helper are not called by these routes; repository methods and PostgreSQL gameplay persistence are not implemented. Proposed AI and history routes are not part of the active route set.

See [game-domain.md](game-domain.md) for the implemented state/rules, [database-design.md](database-design.md) for the schema foundation and open decisions, and [test-plan.md](test-plan.md) for observed test evidence and blockers.
