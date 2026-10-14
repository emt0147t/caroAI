"""
Task D — Win detection tests theo bốn hướng.

Kiểm tra hàm evaluate_line và evaluate_board phát hiện PPPPP
(5 quân liên tiếp) đúng trên 4 hướng:
1. Ngang (horizontal)
2. Dọc (vertical)
3. Chéo chính \\
4. Chéo phụ /

Luật thắng dự án: >=5 quân liên tiếp cùng màu (được xác nhận tại
app/domain/game_rules.py và evaluator.py SCORE_FIVE = 100_000_000).
"""

import pytest
from app.ai.evaluator import evaluate_board, evaluate_line, SCORE_FIVE

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


# ── D.1  evaluate_line — phát hiện PPPPP ─────────────────────────────────────

def test_five_in_a_row_line():
    """evaluate_line([1,1,1,1,1]) phải trả về SCORE_FIVE."""
    line = [PLAYER_X] * 5
    assert evaluate_line(line, PLAYER_X) == SCORE_FIVE


def test_five_in_a_row_with_extra():
    """Chuỗi 6 quân liên tiếp cũng phải phát hiện PPPPP."""
    line = [PLAYER_X] * 6
    assert evaluate_line(line, PLAYER_X) >= SCORE_FIVE


def test_four_in_a_row_not_five():
    """4 quân không đủ thắng."""
    line = [PLAYER_X] * 4
    assert evaluate_line(line, PLAYER_X) < SCORE_FIVE


def test_broken_chain_not_five():
    """Chuỗi bị ngắt (4 + 1 quân, cách nhau 1 ô) không phải PPPPP."""
    line = [PLAYER_X, PLAYER_X, PLAYER_X, PLAYER_X, EMPTY, PLAYER_X]
    assert evaluate_line(line, PLAYER_X) < SCORE_FIVE


def test_opponent_piece_breaks_chain():
    """Quân đối thủ chặn chuỗi: không được tính là PPPPP."""
    line = [PLAYER_X, PLAYER_X, PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_X]
    assert evaluate_line(line, PLAYER_X) < SCORE_FIVE


def test_line_too_short():
    """Line < 5 phần tử luôn trả về 0."""
    line = [PLAYER_X, PLAYER_X, PLAYER_X, PLAYER_X]
    assert evaluate_line(line, PLAYER_X) == 0


# ── D.2  evaluate_board — phát hiện thắng theo 4 hướng ───────────────────────

class TestHorizontalWin:
    """D.2.1 Ngang."""

    def test_horizontal_win_middle(self):
        """5 quân nằm ngang ở giữa bàn → evaluate_board >= SCORE_FIVE."""
        b = empty_board()
        for c in range(5, 10):          # cols 5–9
            b[7][c] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_horizontal_win_near_left_edge(self):
        """5 quân nằm ngang gần mép trái (cols 0–4)."""
        b = empty_board()
        for c in range(5):
            b[7][c] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_horizontal_win_near_right_edge(self):
        """5 quân nằm ngang gần mép phải (cols 10–14)."""
        b = empty_board()
        for c in range(10, 15):
            b[7][c] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_horizontal_four_not_win(self):
        """4 quân ngang chưa đủ thắng."""
        b = empty_board()
        for c in range(5, 9):
            b[7][c] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score < SCORE_FIVE

    def test_horizontal_no_chain(self):
        """Bàn trống hoặc quân rời: không phát hiện win."""
        b = empty_board()
        b[7][7] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score < SCORE_FIVE


class TestVerticalWin:
    """D.2.2 Dọc."""

    def test_vertical_win_middle(self):
        """5 quân dọc ở giữa bàn → >= SCORE_FIVE."""
        b = empty_board()
        for r in range(5, 10):
            b[r][7] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_vertical_win_near_top_edge(self):
        """5 quân dọc gần mép trên (rows 0–4)."""
        b = empty_board()
        for r in range(5):
            b[r][7] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_vertical_win_near_bottom_edge(self):
        """5 quân dọc gần mép dưới (rows 10–14)."""
        b = empty_board()
        for r in range(10, 15):
            b[r][7] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_vertical_four_not_win(self):
        """4 quân dọc chưa đủ thắng."""
        b = empty_board()
        for r in range(5, 9):
            b[r][7] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score < SCORE_FIVE


class TestDiagonalMainWin:
    r"""D.2.3 Chéo chính (\)."""

    def test_diagonal_main_win_middle(self):
        r"""5 quân chéo chính ở giữa bàn."""
        b = empty_board()
        for i in range(5):
            b[5 + i][5 + i] = PLAYER_X    # (5,5)…(9,9)
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_main_win_top_left_corner(self):
        r"""5 quân chéo chính từ góc trên trái (0,0)…(4,4)."""
        b = empty_board()
        for i in range(5):
            b[i][i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_main_win_bottom_right_corner(self):
        r"""5 quân chéo chính gần góc dưới phải (10,10)…(14,14)."""
        b = empty_board()
        for i in range(5):
            b[10 + i][10 + i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_main_four_not_win(self):
        r"""4 quân chéo chính chưa đủ thắng."""
        b = empty_board()
        for i in range(4):
            b[5 + i][5 + i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score < SCORE_FIVE


class TestDiagonalAntiWin:
    """D.2.4 Chéo phụ (/)."""

    def test_diagonal_anti_win_middle(self):
        """5 quân chéo phụ ở giữa bàn."""
        b = empty_board()
        for i in range(5):
            b[5 + i][9 - i] = PLAYER_X    # (5,9),(6,8),(7,7),(8,6),(9,5)
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_anti_win_top_right_corner(self):
        """5 quân chéo phụ gần góc trên phải (0,14)…(4,10)."""
        b = empty_board()
        for i in range(5):
            b[i][14 - i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_anti_win_bottom_left_corner(self):
        """5 quân chéo phụ gần góc dưới trái (10,4)…(14,0)."""
        b = empty_board()
        for i in range(5):
            b[10 + i][4 - i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score >= SCORE_FIVE

    def test_diagonal_anti_four_not_win(self):
        """4 quân chéo phụ chưa đủ thắng."""
        b = empty_board()
        for i in range(4):
            b[5 + i][9 - i] = PLAYER_X
        score = evaluate_board(b, PLAYER_X, PLAYER_O)
        assert score < SCORE_FIVE


# ── D.3  Phát hiện đúng người thắng ─────────────────────────────────────────

def test_detects_ai_win_not_human():
    """Chuỗi 5 của AI phải cho score dương, không phát hiện Human thắng."""
    b = empty_board()
    for c in range(5, 10):
        b[7][c] = PLAYER_X
    score = evaluate_board(b, PLAYER_X, PLAYER_O)
    # score phải dương (AI thắng)
    assert score > 0

    # Nếu xem từ góc nhìn PLAYER_O (human), score phải âm (AI bị lợi)
    score_human_pov = evaluate_board(b, PLAYER_O, PLAYER_X)
    assert score_human_pov < 0


def test_no_false_positive_on_empty_board():
    """Board trống không được phát hiện thắng."""
    b = empty_board()
    score = evaluate_board(b, PLAYER_X, PLAYER_O)
    assert score == 0
