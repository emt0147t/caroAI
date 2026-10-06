import pytest
from app.ai.move_generator import get_candidate_moves

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def test_empty_board_returns_center():
    """Nếu bàn cờ trống hoàn toàn, AI phải chọn ô trung tâm (7, 7)."""
    board = create_empty_board()
    candidates = get_candidate_moves(board)
    assert candidates == [(7, 7)]

def test_candidates_around_single_stone():
    """Nếu chỉ có 1 quân cờ tại (7, 7), các candidate chỉ nằm trong bán kính lân cận."""
    board = create_empty_board()
    board[7][7] = PLAYER_X
    candidates = get_candidate_moves(board, radius=1)
    
    # 8 ô xung quanh (7,7)
    expected = {
        (6, 6), (6, 7), (6, 8),
        (7, 6),         (7, 8),
        (8, 6), (8, 7), (8, 8)
    }
    assert set(candidates) == expected
    assert (7, 7) not in candidates  # Ô đã có quân không được là candidate

def test_no_out_of_bounds_candidates():
    """Quân cờ nằm ở góc (0, 0) không được sinh candidate có tọa độ âm."""
    board = create_empty_board()
    board[0][0] = PLAYER_X
    candidates = get_candidate_moves(board, radius=1)
    
    expected = {(0, 1), (1, 0), (1, 1)}
    assert set(candidates) == expected