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

## Planned interfaces — not implemented in this branch

The following designs are retained for M1/M2 review. They must not be treated as callable routes or finalized contracts until their owners confirm and implement them:

| Proposed interface | Status / dependency |
|---|---|
| `POST /api/games/{game_id}/ai-move` | Not implemented. Requires M1 route/game contract and M2 AI integration. |
| `POST /api/games/{game_id}/hint` | Not implemented. Requires M1/M2 contract and AI integration. |
| `POST /api/games/{game_id}/analysis` | Not implemented. Requires M1/M2 contract and AI integration. |
| `GET /api/history` | Not implemented. Persistence and response contract require M1 database integration. |

Previous request/response examples for these interfaces were design sketches only. Their payloads, status codes, difficulty values, persistence behavior, and response fields remain subject to owner review.

The sketches below preserve the earlier design intent; they are **non-normative and unimplemented**:

#### Proposed AI move sketch

`POST /api/games/{game_id}/ai-move` was sketched with a difficulty request and a move plus updated game response:

```json
{"difficulty": "medium"}
```

```json
{"move": {"row": 6, "col": 8, "player": "O", "move_number": 2}, "game": "<proposed GameResponse>"}
```

#### Proposed hint and analysis sketches

```text
POST /api/games/{game_id}/hint
Request sketch:  {"difficulty": "medium"}
Response sketch: {"suggested_move": {"row": 7, "col": 9}, "score": 12.5, "model": "minimax"}

POST /api/games/{game_id}/analysis
Request sketch:  {"row": 7, "col": 8}
Response sketch: {"score": 8.5, "best_move": {"row": 7, "col": 9}, "comment": "Move is playable but not optimal."}
```

M1 and M2 must confirm whether these paths and fields remain valid before implementation or client use. These examples do not establish current status codes, difficulty validation, scoring behavior, or AI quality criteria.

#### Proposed history and architecture

`GET /api/history` was sketched to return a games collection, but its filtering, ordering, ownership, and persistence contract is not defined. The previous layered diagram (routes → service/domain → AI/repository → PostgreSQL) is a target design only: the implemented game routes currently call the in-memory service and do not call AI or the database.

## Error response format

Implemented error responses use FastAPI's standard JSON shape:

```json
{"detail": "Human-readable error message"}
```

The implemented game routes use `400` for invalid game actions, `404` for missing games, and `422` for request validation. The exact `404` detail includes the requested game ID as shown above.

## Runtime boundary

Implemented routes → `GameService` → domain rules/state. `GameService` stores state in a process-local dictionary. The SQLAlchemy models/session helper are not called by these routes; repository methods and PostgreSQL gameplay persistence are not implemented. Proposed AI and history routes are not part of the active route set.

See [game-domain.md](game-domain.md) for the implemented state/rules, [database-design.md](database-design.md) for the schema foundation and open decisions, and [test-plan.md](test-plan.md) for observed test evidence and blockers.
