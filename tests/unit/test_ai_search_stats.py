import pytest

from app.ai.engine import get_ai_move
from app.ai.minimax import find_best_move
from app.ai.search_stats import SearchStats


def empty_board():
    return [[0 for _ in range(15)] for _ in range(15)]


def test_search_stats_derive_branching_and_pruning_rates():
    stats = SearchStats()
    stats.generated_candidates = 30
    stats.candidate_cap_considered = 30
    stats.candidate_cap_pruned = 10
    stats.expanded_candidates = 8
    stats.alpha_beta_pruned = 4
    stats.branching_factor_sum = 12
    stats.branching_factor_nodes = 3
    stats.max_branching_factor = 6

    assert stats.average_branching_factor == pytest.approx(4.0)
    assert stats.candidate_cap_pruning_rate == pytest.approx(1 / 3)
    assert stats.alpha_beta_pruning_rate == pytest.approx(0.5)


def test_minimax_populates_nodes_branching_and_pruning_stats():
    board = empty_board()
    board[7][7] = 1
    board[7][8] = 2
    stats = SearchStats()

    move, _score = find_best_move(
        board, ai_player=1, depth=3, candidate_limit=6, stats=stats
    )

    assert move is not None
    assert stats.nodes > 0
    assert stats.leaves > 0
    assert stats.generated_candidates >= stats.expanded_candidates
    assert stats.max_branching_factor <= 6
    assert 0.0 <= stats.alpha_beta_pruning_rate <= 1.0
    assert 0.0 <= stats.candidate_cap_pruning_rate <= 1.0


def test_time_budget_returns_legal_fallback_and_marks_timeout():
    board = empty_board()
    board[7][7] = 1
    original = [row[:] for row in board]

    result = get_ai_move(
        board, ai_player=2, difficulty="impossible", time_budget_ms=0
    )

    assert 0 <= result["row"] < 15
    assert 0 <= result["col"] < 15
    assert board[result["row"]][result["col"]] == 0
    assert result["search_stats"]["timed_out"] is True
    assert result["search_stats"]["shortcut"] == "none"
    assert board == original


def test_mandatory_root_win_shortcut_is_not_lost_to_zero_budget():
    board = empty_board()
    for col in range(3, 7):
        board[7][col] = 2
    result = get_ai_move(
        board, ai_player=2, difficulty="impossible", time_budget_ms=0
    )

    assert (result["row"], result["col"]) in {(7, 2), (7, 7)}
    assert result["search_stats"]["timed_out"] is False
    assert result["search_stats"]["shortcut"] == "immediate_win"
