import pytest
from app.ai.minimax import find_best_move

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def test_minimax_takes_immediate_win():
    """AI (PLAYER_O) phải đi ngay vào ô kết thúc để tạo chuỗi 5 quân thắng cuộc."""
    board = create_empty_board()
    # O đã có 4 quân: (7, 3), (7, 4), (7, 5), (7, 6). Ô (7, 7) đang trống
    for c in range(3, 7):
        board[7][c] = PLAYER_O
        
    best_move, score = find_best_move(board, ai_player=PLAYER_O, depth=2)
    assert best_move == (7, 7) or best_move == (7, 2)

def test_minimax_blocks_opponent_four():
    """AI (PLAYER_O) phải chặn ngay khi đối thủ X đã có 4 quân nguy hiểm."""
    board = create_empty_board()
    # Đối thủ X có 4 quân: (7, 3), (7, 4), (7, 5), (7, 6)
    for c in range(3, 7):
        board[7][c] = PLAYER_X
    # AI có 1 quân rời rạc ở chỗ khác
    board[0][0] = PLAYER_O

    best_move, score = find_best_move(board, ai_player=PLAYER_O, depth=2)
    # AI buộc phải đi vào 1 trong 2 đầu (7, 2) hoặc (7, 7) để chặn
    assert best_move in [(7, 2), (7, 7)]
