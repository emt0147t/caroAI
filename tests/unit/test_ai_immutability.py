"""
Task B2 — Board immutability tests.

Đảm bảo các hàm AI (find_best_move, get_ai_move) không mutate
board đầu vào sau khi tìm kiếm.
"""

import copy
from app.ai.engine import get_ai_move
from app.ai.minimax import find_best_move

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


# ── B2.1  find_best_move không mutate board ───────────────────────────────────

def test_find_best_move_does_not_mutate_empty_board():
    """find_best_move trên bàn cờ trống không được thay đổi board."""
    b = empty_board()
    b_before = copy.deepcopy(b)
    find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert b == b_before, "find_best_move mutated the board (empty board case)"


def test_find_best_move_does_not_mutate_mid_game_board():
    """find_best_move trong ván đang chơi không được thay đổi board."""
    b = empty_board()
    # Một số nước đi giữa ván
    positions = [
        (7, 7, PLAYER_X), (7, 8, PLAYER_O),
        (6, 7, PLAYER_X), (8, 7, PLAYER_O),
        (6, 6, PLAYER_X), (8, 8, PLAYER_O),
    ]
    for r, c, p in positions:
        b[r][c] = p
    b_before = copy.deepcopy(b)
    find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert b == b_before, "find_best_move mutated the board (mid-game case)"


def test_find_best_move_does_not_mutate_near_winning_board():
    """find_best_move khi AI sắp thắng không được để lại dấu vết trên board."""
    b = empty_board()
    for c in range(3, 7):       # AI có 4 quân nằm ngang
        b[7][c] = PLAYER_X
    b_before = copy.deepcopy(b)
    find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert b == b_before, "find_best_move mutated the board (near-win case)"


def test_find_best_move_does_not_mutate_depth3():
    """find_best_move ở depth=3 không được mutate board."""
    b = empty_board()
    b[7][7] = PLAYER_O
    b[7][8] = PLAYER_X
    b_before = copy.deepcopy(b)
    find_best_move(b, ai_player=PLAYER_X, depth=3)
    assert b == b_before, "find_best_move mutated the board (depth=3)"


# ── B2.2  get_ai_move (engine) không mutate board ────────────────────────────

def test_get_ai_move_does_not_mutate_board_easy():
    """get_ai_move(EASY) không được thay đổi board đầu vào."""
    b = empty_board()
    b[7][7] = PLAYER_O
    b_before = copy.deepcopy(b)
    get_ai_move(b, ai_player=PLAYER_X, difficulty="EASY")
    assert b == b_before, "get_ai_move(EASY) mutated the board"


def test_get_ai_move_does_not_mutate_board_medium():
    """get_ai_move(MEDIUM) không được thay đổi board đầu vào."""
    b = empty_board()
    b[7][7] = PLAYER_O
    b_before = copy.deepcopy(b)
    get_ai_move(b, ai_player=PLAYER_X, difficulty="MEDIUM")
    assert b == b_before, "get_ai_move(MEDIUM) mutated the board"


def test_get_ai_move_does_not_mutate_board_hard():
    """get_ai_move(HARD) không được thay đổi board đầu vào."""
    b = empty_board()
    b[7][7] = PLAYER_O
    b_before = copy.deepcopy(b)
    get_ai_move(b, ai_player=PLAYER_X, difficulty="HARD")
    assert b == b_before, "get_ai_move(HARD) mutated the board"
