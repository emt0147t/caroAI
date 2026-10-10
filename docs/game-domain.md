# CaroAI Game Domain — Current Implementation

This document describes the domain code currently present in this branch: `app/domain/game_state.py` and `app/domain/game_rules.py`. It does not define API behavior beyond the domain objects, and it does not imply persistence. `GameService` currently keeps each `GameState` in process memory.

## Domain concepts

### Game state

`GameState` contains:

- a 15 × 15 board, initialized with the string `EMPTY` in every cell;
- `current_player`, initially `Player.X`;
- `mode`, one of `HUMAN_VS_HUMAN` or `HUMAN_VS_AI`;
- `status`, initially `IN_PROGRESS`;
- `move_count`, initially zero;
- `winner`, initially `None`.

The implementation currently has no domain fields for a creation/end timestamp or a persisted result record.

### Players and moves

`Player` has values `X` and `O`. A `Move` is an immutable value containing `row`, `col`, the player who placed the mark, and a one-based `move_number`. `GameRules.apply_move` selects the player from `state.current_player`, writes that mark to the board, and increments `move_count`.

For a non-terminal move, the next player alternates between X and O. The domain code applies the same turn mechanism regardless of `mode`; selecting `HUMAN_VS_AI` does not itself invoke an AI move.

## Implemented rules

- Valid board coordinates are rows and columns `0..14`, inclusive.
- A move is rejected if either coordinate is outside the board, the target cell is occupied, or the game is no longer `IN_PROGRESS`. These conditions raise `InvalidMoveError`.
- A player wins when their mark forms a contiguous line of **at least five** through the latest move, horizontally, vertically, or on either diagonal.
- A winning move sets status to `X_WON` or `O_WON` and sets `winner` to that player.
- If the move count reaches 225 and that move did not win, status becomes `DRAW`.
- A terminal game rejects later moves.

`GameRules` evaluates a win from the latest move and does not independently validate the history/legality of a board that callers have manually constructed. A draw is determined from the move count and win check at application time.

## Tests and evidence

The current domain regression file is `tests/test_game_rules.py`; it covers initialization, legal/occupied/out-of-bounds moves, four win directions, draw, and post-win rejection. The recorded observed result is 14 passed on Windows CPython 3.13.15. Python 3.11 has not been verified; see [test-plan.md](test-plan.md).

Service and API behavior are covered separately in `tests/test_game_service.py` and `tests/test_games_api.py`. Those layers currently use the same in-memory state and do not establish database persistence.

## Decisions for M1 review

- Confirm whether `HUMAN_VS_AI` should permit the same human move alternation currently used by the domain or should be integrated with a separate AI turn flow.
- Confirm the authoritative game/result vocabulary and whether domain/runtime state needs `result`, `ended_at`, or other terminal metadata.
- Confirm whether the current at-least-five rule and full-board draw rule are the intended product rules.
- Confirm game ID semantics and lifecycle when database persistence is integrated; API/database ID mapping is not defined by this domain module.

These are review questions, not additional rules. The domain documentation does not prescribe database schema, API payloads, AI behavior, or persistence.
