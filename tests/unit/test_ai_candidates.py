"""
Task C — Candidate moves legality tests.

Kiểm tra:
- Nước đi nằm trong giới hạn bàn cờ 15×15.
- Nước đi nằm trên ô trống.
- Không có candidate trùng lặp.
- Bán kính Chebyshev R=1 và R=2.
- Các trường hợp biên: góc, mép, bàn cờ rỗng, bàn cờ gần đầy.
"""

from app.ai.move_generator import get_candidate_moves, BOARD_SIZE, EMPTY

PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


# ── C.1  Board rỗng ──────────────────────────────────────────────────────────

def test_empty_board_center():
    """Board trống → trả về đúng ô trung tâm (7, 7)."""
    b = empty_board()
    result = get_candidate_moves(b)
    assert result == [(7, 7)]


# ── C.2  In-bounds (R=1) ─────────────────────────────────────────────────────

def test_all_candidates_in_bounds_r1():
    """Mọi candidate với R=1 phải nằm trong [0, 14]."""
    b = empty_board()
    b[0][0] = PLAYER_X
    for r, c in get_candidate_moves(b, radius=1):
        assert 0 <= r < BOARD_SIZE, f"Row {r} out of bounds"
        assert 0 <= c < BOARD_SIZE, f"Col {c} out of bounds"


def test_all_candidates_in_bounds_r2():
    """Mọi candidate với R=2 phải nằm trong [0, 14]."""
    b = empty_board()
    b[0][0] = PLAYER_X
    for r, c in get_candidate_moves(b, radius=2):
        assert 0 <= r < BOARD_SIZE, f"Row {r} out of bounds"
        assert 0 <= c < BOARD_SIZE, f"Col {c} out of bounds"


def test_all_candidates_in_bounds_bottom_right_corner():
    """Quân ở góc (14, 14): mọi candidate phải nằm trong [0, 14]."""
    b = empty_board()
    b[14][14] = PLAYER_X
    for r, c in get_candidate_moves(b, radius=2):
        assert 0 <= r < BOARD_SIZE
        assert 0 <= c < BOARD_SIZE


def test_all_candidates_in_bounds_top_right_corner():
    """Quân ở góc (0, 14)."""
    b = empty_board()
    b[0][14] = PLAYER_X
    for r, c in get_candidate_moves(b, radius=2):
        assert 0 <= r < BOARD_SIZE
        assert 0 <= c < BOARD_SIZE


def test_all_candidates_in_bounds_bottom_left_corner():
    """Quân ở góc (14, 0)."""
    b = empty_board()
    b[14][0] = PLAYER_X
    for r, c in get_candidate_moves(b, radius=2):
        assert 0 <= r < BOARD_SIZE
        assert 0 <= c < BOARD_SIZE


# ── C.3  Candidates chỉ trên ô trống ────────────────────────────────────────

def test_candidates_are_empty_cells_only():
    """Không được có candidate nằm trên ô đã có quân."""
    b = empty_board()
    b[7][7] = PLAYER_X
    b[7][8] = PLAYER_O
    candidates = get_candidate_moves(b, radius=1)
    for r, c in candidates:
        assert b[r][c] == EMPTY, f"Candidate ({r},{c}) is occupied: {b[r][c]}"


def test_candidates_empty_cells_r2():
    """R=2: không candidate nào nằm trên ô đã có quân."""
    b = empty_board()
    for r in range(5, 10):
        for c in range(5, 10):
            b[r][c] = PLAYER_X if (r + c) % 2 == 0 else PLAYER_O
    candidates = get_candidate_moves(b, radius=2)
    for r, c in candidates:
        assert b[r][c] == EMPTY, f"Candidate ({r},{c}) is occupied"


# ── C.4  Không có candidate trùng lặp ───────────────────────────────────────

def test_no_duplicate_candidates_r1():
    """R=1: danh sách candidate không có phần tử trùng."""
    b = empty_board()
    b[7][7] = PLAYER_X
    b[7][8] = PLAYER_O
    candidates = get_candidate_moves(b, radius=1)
    assert len(candidates) == len(set(candidates)), "Duplicate candidates found (R=1)"


def test_no_duplicate_candidates_r2():
    """R=2: không có candidate trùng lặp."""
    b = empty_board()
    b[5][5] = PLAYER_X
    b[9][9] = PLAYER_O
    candidates = get_candidate_moves(b, radius=2)
    assert len(candidates) == len(set(candidates)), "Duplicate candidates found (R=2)"


def test_no_duplicate_candidates_many_stones():
    """Nhiều quân chồng chéo radius: không được có candidate trùng."""
    b = empty_board()
    for i in range(5):
        b[7][i * 2] = PLAYER_X
    candidates = get_candidate_moves(b, radius=1)
    assert len(candidates) == len(set(candidates))


# ── C.5  Chebyshev R=1 – xác minh tập candidate đúng ─────────────────────────

def test_r1_correct_neighbors_center():
    """R=1 xung quanh quân ở (7, 7): phải có đúng 8 ô lân cận."""
    b = empty_board()
    b[7][7] = PLAYER_X
    candidates = set(get_candidate_moves(b, radius=1))
    expected = {
        (6, 6), (6, 7), (6, 8),
        (7, 6),         (7, 8),
        (8, 6), (8, 7), (8, 8),
    }
    assert candidates == expected


def test_r1_correct_neighbors_top_left_corner():
    """R=1 tại góc (0, 0): chỉ có 3 ô hợp lệ."""
    b = empty_board()
    b[0][0] = PLAYER_X
    candidates = set(get_candidate_moves(b, radius=1))
    expected = {(0, 1), (1, 0), (1, 1)}
    assert candidates == expected


def test_r1_correct_neighbors_top_edge():
    """R=1 tại mép trên (0, 7): chỉ có 5 ô hợp lệ."""
    b = empty_board()
    b[0][7] = PLAYER_X
    candidates = set(get_candidate_moves(b, radius=1))
    expected = {(0, 6), (0, 8), (1, 6), (1, 7), (1, 8)}
    assert candidates == expected


# ── C.6  Chebyshev R=2 – xác minh tập candidate đúng ─────────────────────────

def test_r2_correct_size_center():
    """R=2 xung quanh (7, 7): phải có 24 ô trống (5×5 – 1 quân)."""
    b = empty_board()
    b[7][7] = PLAYER_X
    candidates = get_candidate_moves(b, radius=2)
    assert len(candidates) == 24, f"Expected 24 candidates for R=2 center, got {len(candidates)}"


def test_r2_does_not_include_occupied():
    """R=2: các ô đã có quân không được xuất hiện trong candidate."""
    b = empty_board()
    b[7][7] = PLAYER_X
    b[7][8] = PLAYER_O         # ô trong vùng R=2
    candidates = get_candidate_moves(b, radius=2)
    assert (7, 7) not in candidates
    assert (7, 8) not in candidates


# ── C.7  Board gần đầy ───────────────────────────────────────────────────────

def test_nearly_full_board_returns_remaining_empty():
    """Board gần đầy: candidate = đúng những ô trống còn lại."""
    b = empty_board()
    empty_pos = {(7, 7), (8, 8)}
    val = PLAYER_X
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) not in empty_pos:
                b[r][c] = val
                val = PLAYER_O if val == PLAYER_X else PLAYER_X
    candidates = set(get_candidate_moves(b, radius=1))
    # Candidates phải là tập con của ô trống còn lại
    for r, c in candidates:
        assert b[r][c] == EMPTY, f"Candidate ({r},{c}) is not empty"
