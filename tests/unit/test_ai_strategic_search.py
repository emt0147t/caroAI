"""Tests for tactical profiles and bounded search behaviour."""

from app.ai.strategic_search import (
    _board_key,
    _position_score,
    _threat_features,
    find_strategic_move,
)
from app.ai.evaluator import get_board_raw_scores

N = 15
EMPTY = 0
X = 1
O = 2


def empty_board():
    return [[EMPTY] * N for _ in range(N)]


def test_open_four_has_two_distinct_winning_cells():
    board = empty_board()
    for col in range(4, 8):
        board[7][col] = X

    wins, open_threes, broken_threes = _threat_features(_board_key(board), X)

    assert set(wins) == {(7, 3), (7, 8)}


def test_double_threat_is_scored_above_single_open_four():
    single = empty_board()
    for col in range(4, 8):
        single[7][col] = X

    double = empty_board()
    for col in range(4, 8):
        double[7][col] = X
        double[col][5] = X

    single_scores = get_board_raw_scores(single)
    double_scores = get_board_raw_scores(double)
    single_value = _position_score(_board_key(single), *single_scores, ai_player=X)
    double_value = _position_score(_board_key(double), *double_scores, ai_player=X)

    assert double_value > single_value


def test_single_immediate_threat_is_forced_to_be_blocked():
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = O
    board[0][0] = X

    move, score, stats = find_strategic_move(
        board,
        ai_player=X,
        max_depth=6,
        candidate_limit=10,
        time_budget_ms=300,
        node_budget=12000,
    )

    assert move in {(7, 2), (7, 7)}
    assert board[7][move[1]] == EMPTY
    assert stats["depth"] == 0


def test_search_returns_a_legal_move_under_a_tiny_budget():
    board = empty_board()
    positions = [
        (7, 7, X), (7, 8, O), (6, 7, X), (8, 7, O),
        (6, 6, X), (8, 8, O), (7, 6, O), (6, 8, X),
    ]
    for row, col, player in positions:
        board[row][col] = player

    move, score, stats = find_strategic_move(
        board,
        ai_player=X,
        max_depth=8,
        candidate_limit=10,
        time_budget_ms=20,
        node_budget=1000,
    )

    row, col = move
    assert 0 <= row < N and 0 <= col < N
    assert board[row][col] == EMPTY
