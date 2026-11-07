"""Tests for strong AI behavior, bounded latency, and immutability."""

import copy

import app.ai.engine as engine


BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def test_impossible_uses_iterative_search_and_budget(monkeypatch):
    board = empty_board()
    board[7][7] = PLAYER_O
    captured = {}

    def fake_search(
        board,
        ai_player,
        max_depth,
        candidate_limit,
        time_budget_ms,
        node_budget,
        diversify,
        stats=None,
    ):
        captured.update(
            ai_player=ai_player,
            max_depth=max_depth,
            candidate_limit=candidate_limit,
            time_budget_ms=time_budget_ms,
            node_budget=node_budget,
            diversify=diversify,
        )
        return (7, 8), 123, {"depth": 3, "nodes": 50}

    monkeypatch.setattr(engine, "find_strategic_move", fake_search)
    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="ImPoSsIbLe")

    assert captured == {
        "ai_player": PLAYER_X,
        "max_depth": 8,
        "candidate_limit": 10,
        "time_budget_ms": 700,
        "node_budget": 40000,
        "diversify": True,
    }
    assert (result["row"], result["col"]) == (7, 8)


def test_impossible_takes_an_immediate_win():
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = PLAYER_X

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="impossible")

    assert (result["row"], result["col"]) in {(7, 2), (7, 7)}


def test_impossible_blocks_a_unique_immediate_win():
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = PLAYER_O
    board[7][2] = PLAYER_X

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="IMPOSSIBLE")

    assert (result["row"], result["col"]) == (7, 7)


def test_impossible_midgame_search_returns_legal_move_and_preserves_board():
    board = empty_board()
    positions = [
        (7, 7, PLAYER_X), (7, 8, PLAYER_O),
        (6, 7, PLAYER_X), (8, 7, PLAYER_O),
        (6, 6, PLAYER_X), (8, 8, PLAYER_O),
        (7, 6, PLAYER_O), (6, 8, PLAYER_X),
    ]
    for row, col, player in positions:
        board[row][col] = player
    original = copy.deepcopy(board)

    result = engine.get_ai_move(board, ai_player=PLAYER_X, difficulty="impossible")

    row, col = result["row"], result["col"]
    assert 0 <= row < BOARD_SIZE
    assert 0 <= col < BOARD_SIZE
    assert board[row][col] == EMPTY
    assert board == original
    assert result["elapsed_ms"] < 1200, (
        f"Impossible took {result['elapsed_ms']} ms; expected a bounded sub-1.2s response"
    )


def test_impossible_time_budget_is_enforced_and_reported():
    board = empty_board()
    positions = [
        (7, 7, PLAYER_X), (7, 8, PLAYER_O),
        (6, 7, PLAYER_X), (8, 7, PLAYER_O),
        (6, 6, PLAYER_X), (8, 8, PLAYER_O),
        (7, 6, PLAYER_O), (6, 8, PLAYER_X),
    ]
    for row, col, player in positions:
        board[row][col] = player

    result = engine.get_ai_move(
        board,
        ai_player=PLAYER_X,
        difficulty="impossible",
        time_budget_ms=0,
    )

    assert result["search_stats"]["timed_out"] is True
    assert result["search_stats"]["shortcut"] == "none"
    assert 0 <= result["row"] < BOARD_SIZE
    assert 0 <= result["col"] < BOARD_SIZE
