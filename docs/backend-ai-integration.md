# Backend ↔ AI Integration Contract

## Scope

This document freezes the Sprint 2 contract between the authoritative Backend game domain and the Sprint 1 AI Engine.

## Ownership

The Backend owns the authoritative `GameState` and is the only layer allowed to mutate it through `GameRules`.

The AI Engine is a stateless decision-maker. It receives a board snapshot and returns a proposed coordinate.

The AI must not:
- mutate Backend `GameState`;
- decide whose turn it is;
- apply a move to Backend state;
- determine authoritative win/draw status.

## Board Adapter

Backend board values:

```text
EMPTY -> "EMPTY"
X     -> "X"
O     -> "O"
```

AI board values:

```text
EMPTY -> 0
X     -> 1
O     -> 2
```

The conversion is implemented in `app/ai/adapter.py`.

The adapter creates an independent 15x15 snapshot. Backend and AI representations must not share the same mutable board object.

## AI Engine Input / Output

Input:

```python
{
    "board": list[list[int]],
    "ai_player": 2,
    "difficulty": "easy" | "medium" | "hard"
}
```

Output:

```python
{
    "row": int,
    "col": int,
    "score": int,
    "elapsed_ms": float
}
```

Only `row` and `col` are used by Backend to apply the move. Other fields are AI metadata.

## Backend AI-Move Flow

```text
POST /api/games/{game_id}/ai-move
        |
        v
API Route
        |
        v
GameService.make_ai_move()
        |
        +--> validate game exists
        +--> require HUMAN_VS_AI
        +--> require AI turn (O)
        +--> validate difficulty
        |
        v
board_to_ai(GameState.board)
        |
        v
AI Engine
        |
        v
validate returned row/col
        |
        v
GameRules.validate_move()
        |
        v
GameRules.apply_move()
        |
        v
authoritative GameState
```

## Validation Rules

Backend must reject an AI result when:
- the AI response is not a mapping/object;
- `row` or `col` is missing;
- `row` or `col` is not an integer;
- the coordinate is outside 0..14;
- the selected cell is occupied;
- the game has already finished.

Invalid difficulty values are rejected before the AI Engine is called.

## API Contract

### Request

```http
POST /api/games/{game_id}/ai-move
Content-Type: application/json
```

```json
{
  "difficulty": "medium"
}
```

Allowed values:

```text
easy
medium
hard
```

The default is `medium`.

### Success

HTTP `200`:

```json
{
  "move": {
    "row": 6,
    "col": 8,
    "player": "O",
    "move_number": 2
  },
  "game": {
    "id": "game-id",
    "mode": "HUMAN_VS_AI",
    "status": "IN_PROGRESS",
    "current_player": "X",
    "move_count": 2,
    "winner": null,
    "board": []
  }
}
```

The returned game object is authoritative Backend state after the move.

### Errors

```text
404 - game does not exist
400 - AI move cannot be performed or AI result is illegal
422 - request validation failed
```

API errors use:

```json
{
  "detail": "Human-readable error message"
}
```

## Regression Requirements

The integration suite must cover:
- board mapping in both directions;
- snapshot isolation / AI input immutability;
- normal AI move;
- AI winning move;
- AI blocking move;
- malformed AI output;
- out-of-bounds AI output;
- occupied-cell AI output;
- invalid difficulty;
- HUMAN_VS_HUMAN rejection;
- rejection when it is not the AI turn.

AI tactical correctness remains owned by the AI Engine tests. Backend integration tests verify that valid AI decisions are safely validated and applied without transferring state ownership to AI.
