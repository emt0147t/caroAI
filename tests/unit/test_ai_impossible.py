"""Focused regression tests for the high-budget IMPOSSIBLE AI difficulty."""

import app.ai.engine as engine

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def test_impossible_uses_extended_search_budget(monkeypatch):
    """Engine must route IMPOSSIBLE to depth 4 / candidate limit 20."""
    board = empty_board()
    board[7][7] = PLAYER_O
    captured = {}

    def fake_find_best_move(board, ai_player, depth, candidate_limit):
        captured.update(
            ai_player=ai_player,
            depth=depth,
            candidate_limit=candidate_limit,
        )
        return (7, 8), 123

    monkeypatch.setattr(engine, "find_best_move", fake_find_best_move)

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="ImPoSsIbLe")

    assert captured == {
        "ai_player": PLAYER_X,
        "depth": 4,
        "candidate_limit": 20,
    }
    assert result["row"] == 7
    assert result["col"] == 8


def test_impossible_takes_an_immediate_win():
    """Higher search budget must preserve the engine's immediate-win rule."""
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = PLAYER_X

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="impossible")

    assert (result["row"], result["col"]) in {(7, 2), (7, 7)}
    assert all(board[7][col] == PLAYER_X for col in range(3, 7))


def test_impossible_blocks_an_opponent_immediate_win():
    """Impossible must block a four-in-a-row threat before deeper search."""
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = PLAYER_O
    board[0][0] = PLAYER_X

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="IMPOSSIBLE")

    assert (result["row"], result["col"]) in {(7, 2), (7, 7)}
    assert board[0][0] == PLAYER_X
    assert all(board[7][col] == PLAYER_O for col in range(3, 7))
