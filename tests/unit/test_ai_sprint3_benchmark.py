import copy

import pytest

from app.ai.engine import DIFFICULTY_CONFIG, get_ai_move
from app.ai.evaluator import BOARD_SIZE, EMPTY, has_five_in_a_row
from app.ai.move_generator import get_candidate_moves
from scripts import benchmark_ai_sprint3 as benchmark


def _fixture(name):
    return next(item for item in benchmark.build_fixtures() if item["name"] == name)


def _assert_legal_output(result, board):
    assert isinstance(result, dict)
    assert {"row", "col", "score", "elapsed_ms"} <= set(result)
    row, col = result["row"], result["col"]
    assert isinstance(row, int) and not isinstance(row, bool)
    assert isinstance(col, int) and not isinstance(col, bool)
    assert 0 <= row < BOARD_SIZE
    assert 0 <= col < BOARD_SIZE
    assert board[row][col] == EMPTY
    assert isinstance(result["score"], int)
    assert result["elapsed_ms"] >= 0


def test_sprint3_benchmark_has_at_least_ten_unique_nonterminal_fixtures():
    fixtures = benchmark.build_fixtures()
    assert len(fixtures) >= 10
    assert len({item["name"] for item in fixtures}) == len(fixtures)

    for item in fixtures:
        board = item["board"]
        assert len(board) == BOARD_SIZE
        assert all(len(row) == BOARD_SIZE for row in board)
        assert all(cell in (EMPTY, 1, 2) for row in board for cell in row)
        assert not has_five_in_a_row(board, 1), item["name"]
        assert not has_five_in_a_row(board, 2), item["name"]


def test_full_source_sha_validation_rejects_abbreviated_or_malformed_values():
    assert benchmark.validate_full_sha("A" * 40) == "a" * 40
    with pytest.raises(ValueError, match="full 40-character Git SHA"):
        benchmark.validate_full_sha("1234")
    with pytest.raises(ValueError, match="full 40-character Git SHA"):
        benchmark.validate_full_sha("g" * 40)


def test_nearest_rank_p95_method_is_explicit_and_stable():
    assert benchmark.nearest_rank_percentile([1, 2, 3, 4, 5], 0.95) == 5
    assert benchmark.nearest_rank_percentile([1, 2, 3, 4, 5], 0.50) == 3
    assert benchmark.nearest_rank_percentile([], 0.95) is None
    with pytest.raises(ValueError):
        benchmark.nearest_rank_percentile([1, 2], 0)


@pytest.mark.parametrize("difficulty", list(DIFFICULTY_CONFIG))
def test_demo_ai_win_now_returns_the_only_winning_move(difficulty):
    fixture = _fixture("demo_ai_win_now")
    board = copy.deepcopy(fixture["board"])
    before = copy.deepcopy(board)

    result = get_ai_move(board, fixture["ai_player"], difficulty)
    _assert_legal_output(result, before)

    assert (result["row"], result["col"]) == (7, 7)
    assert board == before


@pytest.mark.parametrize("difficulty", list(DIFFICULTY_CONFIG))
def test_demo_forced_block_returns_the_only_blocking_move(difficulty):
    fixture = _fixture("demo_forced_block")
    board = copy.deepcopy(fixture["board"])
    before = copy.deepcopy(board)

    result = get_ai_move(board, fixture["ai_player"], difficulty)
    _assert_legal_output(result, before)

    assert (result["row"], result["col"]) == (0, 1)
    assert board == before


@pytest.mark.parametrize("difficulty", ["MEDIUM", "HARD"])
def test_demo_midgame_requires_search_and_returns_legal_move(difficulty):
    fixture = _fixture("demo_midgame_search")
    board = copy.deepcopy(fixture["board"])
    before = copy.deepcopy(board)

    result = get_ai_move(board, fixture["ai_player"], difficulty)
    _assert_legal_output(result, before)

    assert board == before
    assert benchmark.has_immediate_win(board, fixture["ai_player"]) is False
    opponent = 2 if fixture["ai_player"] == 1 else 1
    assert benchmark.has_immediate_win(board, opponent) is False


@pytest.mark.parametrize("difficulty", list(DIFFICULTY_CONFIG))
def test_full_board_is_reported_as_controlled_no_legal_move_error(difficulty):
    board = [
        [1 if (row + col) % 2 == 0 else 2 for col in range(BOARD_SIZE)]
        for row in range(BOARD_SIZE)
    ]
    with pytest.raises(ValueError, match="No legal candidate moves"):
        get_ai_move(board, ai_player=1, difficulty=difficulty)


@pytest.mark.parametrize(
    "invalid_move",
    [
        ((15, 7), 10),     # out of bounds
        ((7, -1), 10),     # out of bounds
        ((7, 7), 10),      # occupied cell
        ((None, 7), 10),   # malformed row
        ((7, 8), True),    # malformed score on an otherwise legal empty cell
    ],
)
def test_engine_rejects_malformed_or_illegal_search_result(monkeypatch, invalid_move):
    from app.ai import engine as engine_module

    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    board[7][7] = 2
    move, score = invalid_move
    monkeypatch.setattr(
        engine_module,
        "find_best_move",
        lambda **kwargs: (move, score),
    )
    with pytest.raises(ValueError, match="AI engine returned"):
        engine_module.get_ai_move(board, ai_player=1, difficulty="MEDIUM")


@pytest.mark.parametrize("difficulty", list(DIFFICULTY_CONFIG))
def test_engine_output_contract_and_board_snapshot(difficulty):
    fixture = _fixture("demo_midgame_search")
    board = copy.deepcopy(fixture["board"])
    before = copy.deepcopy(board)

    result = get_ai_move(board, fixture["ai_player"], difficulty)

    _assert_legal_output(result, before)
    assert board == before
    assert len(get_candidate_moves(board, radius=2)) > 0
