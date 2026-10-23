"""
Task E — Difficulty validation tests.

Kiểm tra cách AI engine nhận và xử lý difficulty.

Từ engine.py (source thực tế):
    DIFFICULTY_CONFIG = {
        "EASY":   {"depth": 1, "candidate_limit": 6},
        "MEDIUM": {"depth": 2, "candidate_limit": 10},
        "HARD":   {"depth": 3, "candidate_limit": 14},
    }
    diff_key = difficulty.upper()
    config = DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG["MEDIUM"])

Fallback: giá trị không hợp lệ → MEDIUM (không raise exception).
"""

import pytest
from app.ai.engine import get_ai_move, DIFFICULTY_CONFIG

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def base_board():
    b = empty_board()
    b[7][7] = PLAYER_O
    return b


# ── E.1  DIFFICULTY_CONFIG chứa đúng 3 key hợp lệ ───────────────────────────

def test_difficulty_config_has_easy():
    assert "EASY" in DIFFICULTY_CONFIG


def test_difficulty_config_has_medium():
    assert "MEDIUM" in DIFFICULTY_CONFIG


def test_difficulty_config_has_hard():
    assert "HARD" in DIFFICULTY_CONFIG


def test_difficulty_config_no_extra_keys():
    """Contract chỉ định nghĩa 3 mức độ."""
    assert set(DIFFICULTY_CONFIG.keys()) == {"EASY", "MEDIUM", "HARD"}


# ── E.2  Các key config bắt buộc ─────────────────────────────────────────────

@pytest.mark.parametrize("diff", ["EASY", "MEDIUM", "HARD"])
def test_config_has_depth(diff):
    assert "depth" in DIFFICULTY_CONFIG[diff]


@pytest.mark.parametrize("diff", ["EASY", "MEDIUM", "HARD"])
def test_config_has_candidate_limit(diff):
    assert "candidate_limit" in DIFFICULTY_CONFIG[diff]


@pytest.mark.parametrize("diff", ["EASY", "MEDIUM", "HARD"])
def test_config_depth_is_positive_int(diff):
    depth = DIFFICULTY_CONFIG[diff]["depth"]
    assert isinstance(depth, int) and depth >= 1


@pytest.mark.parametrize("diff", ["EASY", "MEDIUM", "HARD"])
def test_config_candidate_limit_is_positive_int(diff):
    limit = DIFFICULTY_CONFIG[diff]["candidate_limit"]
    assert isinstance(limit, int) and limit >= 1


# ── E.3  Giá trị depth tăng dần theo độ khó ─────────────────────────────────

def test_hard_depth_ge_medium_depth():
    assert DIFFICULTY_CONFIG["HARD"]["depth"] >= DIFFICULTY_CONFIG["MEDIUM"]["depth"]


def test_medium_depth_ge_easy_depth():
    assert DIFFICULTY_CONFIG["MEDIUM"]["depth"] >= DIFFICULTY_CONFIG["EASY"]["depth"]


# ── E.4  Các mức độ hợp lệ — get_ai_move trả về output đúng contract ─────────

@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD"])
def test_valid_difficulty_returns_correct_keys(difficulty):
    """get_ai_move với difficulty hợp lệ → dict đúng contract."""
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert "row" in result
    assert "col" in result
    assert "score" in result
    assert "elapsed_ms" in result


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_lowercase_difficulty_is_accepted(difficulty):
    """Lowercase difficulty ('easy', 'medium', 'hard') phải được chấp nhận (case-insensitive)."""
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert "row" in result
    assert "col" in result


@pytest.mark.parametrize("difficulty", ["Easy", "Medium", "Hard"])
def test_mixed_case_difficulty_is_accepted(difficulty):
    """Mixed-case difficulty phải được chấp nhận."""
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert "row" in result


# ── E.5  Fallback cho giá trị không hợp lệ ───────────────────────────────────

def test_invalid_difficulty_does_not_raise():
    """
    Giá trị difficulty không hợp lệ không được raise exception.
    Engine fallback về MEDIUM theo contract hiện tại.
    """
    b = base_board()
    # Không được raise, phải trả về kết quả hợp lệ
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty="UNKNOWN")
    assert "row" in result
    assert "col" in result


def test_empty_string_difficulty_does_not_raise():
    """Empty string fallback về MEDIUM."""
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty="")
    assert "row" in result


# ── E.6  Output hợp lệ theo contract ─────────────────────────────────────────

@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD"])
def test_output_row_in_bounds(difficulty):
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert 0 <= result["row"] < BOARD_SIZE


@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD"])
def test_output_col_in_bounds(difficulty):
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert 0 <= result["col"] < BOARD_SIZE


@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD"])
def test_output_elapsed_ms_non_negative(difficulty):
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    assert result["elapsed_ms"] >= 0


@pytest.mark.parametrize("difficulty", ["EASY", "MEDIUM", "HARD"])
def test_output_move_on_empty_cell(difficulty):
    """AI phải trả về ô trống."""
    b = base_board()
    result = get_ai_move(b, ai_player=PLAYER_X, difficulty=difficulty)
    r, c = result["row"], result["col"]
    assert b[r][c] == EMPTY, f"AI returned occupied cell ({r},{c}) for {difficulty}"
