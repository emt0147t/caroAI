"""Difficulty configuration and output contract tests."""
import pytest

from app.ai.engine import DIFFICULTY_CONFIG, get_ai_move

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def base_board():
    board = empty_board()
    board[7][7] = PLAYER_O
    return board


def test_difficulty_config_has_exactly_four_levels():
    assert set(DIFFICULTY_CONFIG) == {"EASY", "MEDIUM", "HARD", "IMPOSSIBLE"}


@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD", "IMPOSSIBLE"])
def test_config_has_positive_depth_and_candidate_limit(difficulty):
    config = DIFFICULTY_CONFIG[difficulty]
    assert isinstance(config["depth"], int) and config["depth"] >= 1
    assert isinstance(config["candidate_limit"], int) and config["candidate_limit"] >= 1


@pytest.mark.parametrize("difficulty", ["HARD", "IMPOSSIBLE"])
def test_strong_levels_have_explicit_search_budgets(difficulty):
    config = DIFFICULTY_CONFIG[difficulty]
    assert config["time_budget_ms"] > 0
    assert config["node_budget"] > 0
    assert config["diversify"] is True


def test_depth_increases_with_difficulty():
    assert DIFFICULTY_CONFIG["MEDIUM"]["depth"] >= DIFFICULTY_CONFIG["EASY"]["depth"]
    assert DIFFICULTY_CONFIG["HARD"]["depth"] > DIFFICULTY_CONFIG["MEDIUM"]["depth"]
    assert DIFFICULTY_CONFIG["IMPOSSIBLE"]["depth"] > DIFFICULTY_CONFIG["HARD"]["depth"]


@pytest.mark.parametrize(
    "difficulty",
    ["easy", "medium", "hard", "impossible", "Easy", "Medium", "Hard", "ImPoSsIbLe"],
)
def test_difficulty_is_case_insensitive_and_returns_valid_move(difficulty):
    board = base_board()
    result = get_ai_move(board, ai_player=PLAYER_X, difficulty=difficulty)
    assert 0 <= result["row"] < BOARD_SIZE
    assert 0 <= result["col"] < BOARD_SIZE
    assert board[result["row"]][result["col"]] == EMPTY
    assert result["elapsed_ms"] >= 0


@pytest.mark.parametrize("difficulty", ["UNKNOWN", ""])
def test_unknown_difficulty_falls_back_to_medium(difficulty):
    result = get_ai_move(base_board(), ai_player=PLAYER_X, difficulty=difficulty)
    assert 0 <= result["row"] < BOARD_SIZE
    assert 0 <= result["col"] < BOARD_SIZE


def test_impossible_budget_can_be_overridden_by_argument(monkeypatch):
    monkeypatch.setenv("CAROAI_IMPOSSIBLE_TIME_BUDGET_MS", "900")
    result = get_ai_move(
        base_board(), ai_player=PLAYER_X, difficulty="impossible", time_budget_ms=25
    )
    assert result["elapsed_ms"] < 200


def test_impossible_budget_rejects_invalid_environment_value(monkeypatch):
    monkeypatch.setenv("CAROAI_IMPOSSIBLE_TIME_BUDGET_MS", "not-a-number")
    with pytest.raises(ValueError, match="must be numeric"):
        get_ai_move(base_board(), ai_player=PLAYER_X, difficulty="impossible")
