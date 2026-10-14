"""
Task B1 — Tactical regression tests cho AI engine.

Các fixture kiểm tra:
- AI có nước thắng ngay (win-in-one) → phải chọn nước thắng.
- Đối thủ có nước thắng ngay → AI phải chặn.
- AI ưu tiên thắng hơn chặn khi cả hai có thể xảy ra trong 1 nước.
- Terminal state: bàn cờ gần đầy không crash.
"""

import copy
import pytest
from app.ai.engine import get_ai_move
from app.ai.minimax import find_best_move
from app.ai.evaluator import evaluate_board, SCORE_FIVE

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1  # ai_player trong các test
PLAYER_O = 2  # human / opponent


# ── helpers ──────────────────────────────────────────────────────────────────

def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def board_with(cells: dict) -> list:
    """Tạo board với các ô đã cho: {(r,c): player}."""
    b = empty_board()
    for (r, c), p in cells.items():
        b[r][c] = p
    return b


# ── B1.1  AI có nước thắng ngay → phải lấy ──────────────────────────────────

def test_ai_takes_winning_move_horizontal():
    """AI (P_X) có 4 quân nằm ngang, ô (7,7) trống → phải đi (7,7) hoặc (7,2)."""
    b = empty_board()
    for c in range(3, 7):         # (7,3)…(7,6) = 4 quân
        b[7][c] = PLAYER_X
    move, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move in [(7, 7), (7, 2)], f"Expected winning move, got {move}"
    assert score >= SCORE_FIVE


def test_ai_takes_winning_move_vertical():
    """AI (P_X) có 4 quân dọc, ô (4,7) trống → phải đi (4,7) hoặc (0,7)."""
    b = empty_board()
    for r in range(1, 5):         # rows 1-4, col 7
        b[r][7] = PLAYER_X
    move, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move in [(0, 7), (5, 7)], f"Expected winning move vertical, got {move}"
    assert score >= SCORE_FIVE


def test_ai_takes_winning_move_diagonal_main():
    """AI (P_X) có 4 quân chéo chính \\."""
    b = empty_board()
    for i in range(1, 5):         # (1,1)…(4,4)
        b[i][i] = PLAYER_X
    move, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move in [(0, 0), (5, 5)], f"Expected diagonal win move, got {move}"
    assert score >= SCORE_FIVE


def test_ai_takes_winning_move_diagonal_anti():
    """AI (P_X) có 4 quân chéo phụ /."""
    b = empty_board()
    for i in range(1, 5):         # (1,4)…(4,1)
        b[i][5 - i] = PLAYER_X
    # positions: (1,4),(2,3),(3,2),(4,1) → thêm (0,5) hoặc (5,0)
    move, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move in [(0, 5), (5, 0)], f"Expected anti-diagonal win move, got {move}"
    assert score >= SCORE_FIVE


# ── B1.2  Đối thủ có nước thắng ngay → AI phải chặn ────────────────────────

def test_ai_blocks_opponent_four_horizontal():
    """Đối thủ (P_O) có 4 quân nằm ngang, AI phải chặn."""
    b = empty_board()
    for c in range(3, 7):         # (7,3)…(7,6)
        b[7][c] = PLAYER_O
    b[0][0] = PLAYER_X             # quân rời để candidates không rỗng
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert move in [(7, 2), (7, 7)], f"Expected blocking move, got {move}"


def test_ai_blocks_opponent_four_vertical():
    """Đối thủ (P_O) có 4 quân dọc, AI phải chặn."""
    b = empty_board()
    for r in range(1, 5):
        b[r][7] = PLAYER_O
    b[0][0] = PLAYER_X
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert move in [(0, 7), (5, 7)], f"Expected blocking vertical, got {move}"


def test_ai_blocks_opponent_four_diagonal_main():
    """Đối thủ (P_O) có 4 quân chéo chính, AI phải chặn."""
    b = empty_board()
    for i in range(1, 5):
        b[i][i] = PLAYER_O
    b[0][14] = PLAYER_X
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert move in [(0, 0), (5, 5)], f"Expected diagonal block, got {move}"


def test_ai_blocks_opponent_four_diagonal_anti():
    """Đối thủ (P_O) có 4 quân chéo phụ, AI phải chặn."""
    b = empty_board()
    for i in range(1, 5):
        b[i][5 - i] = PLAYER_O
    b[0][14] = PLAYER_X
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert move in [(0, 5), (5, 0)], f"Expected anti-diagonal block, got {move}"


# ── B1.3  AI ưu tiên thắng trước khi chặn ────────────────────────────────────

def test_ai_prefers_win_over_block():
    """
    AI (P_X) có nước thắng ngay VÀ đối thủ P_O có 3 quân (chưa đủ thắng).
    AI phải chọn nước thắng, không phải chặn.

    NOTE: evaluate_board trả về (ai_score - 1.2 * human_score), nên score
    thực tế khi thắng có thể nhỏ hơn SCORE_FIVE một chút do trừ đi
    điểm heuristic của đối thủ. Threshold 0.9 * SCORE_FIVE (90M) vẫn là
    "winning territory" rõ ràng và phản ánh đúng giới hạn thiết kế.
    """
    b = empty_board()
    for c in range(3, 7):         # AI sẵn có 4 quân ngang
        b[7][c] = PLAYER_X
    for r in range(5, 8):          # O có 3 quân dọc – chưa đủ tạo 5
        b[r][0] = PLAYER_O
    move, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move in [(7, 2), (7, 7)], f"AI phải thắng ngay, got {move}"
    # 0.9 * SCORE_FIVE phản ánh evaluate_board có thể trừ human pattern score
    assert score >= int(SCORE_FIVE * 0.9), (
        f"Score {score} quá thấp so với ngưỡng winning ({int(SCORE_FIVE * 0.9)})"
    )


# ── B1.4  Terminal / near-full board ─────────────────────────────────────────

def test_near_full_board_does_not_crash():
    """Bàn cờ gần đầy (chỉ còn 1 ô trống) không crash."""
    b = empty_board()
    val = PLAYER_X
    empty_pos = (14, 14)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) == empty_pos:
                continue
            b[r][c] = val
            val = PLAYER_O if val == PLAYER_X else PLAYER_X
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert move is not None


def test_invalid_move_not_returned():
    """AI không được trả về tọa độ nằm ngoài bàn cờ."""
    b = empty_board()
    b[7][7] = PLAYER_O
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert move is not None
    r, c = move
    assert 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE, f"Out-of-bounds move: {move}"
    assert b[r][c] == EMPTY, f"Move lands on occupied cell: {move}"
