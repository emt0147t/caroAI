import pytest
from app.ai.evaluator import evaluate_board, evaluate_line

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def test_five_in_a_row_score():
    """Chuỗi 5 quân liên tiếp phải có điểm số chiến thắng cực lớn."""
    line = [PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O]
    score = evaluate_line(line, player=PLAYER_O)
    assert score >= 100_000_000

def test_open_four_score_higher_than_open_three():
    """4 quân mở 2 đầu (.XXXX.) phải có điểm cao hơn nhiều so với 3 quân mở (.XXX.)."""
    open_four = [EMPTY, PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O, EMPTY]
    open_three = [EMPTY, PLAYER_O, PLAYER_O, PLAYER_O, EMPTY]
    
    score_four = evaluate_line(open_four, player=PLAYER_O)
    score_three = evaluate_line(open_three, player=PLAYER_O)
    
    assert score_four > score_three * 10

def test_evaluate_board_favors_winning_player():
    """Bàn cờ có thế cờ mạnh của AI (PLAYER_O) phải có điểm dương lớn."""
    board = create_empty_board()
    for c in range(5, 9):
        board[7][c] = PLAYER_O
        
    score = evaluate_board(board, ai_player=PLAYER_O, human_player=PLAYER_X)
    assert score > 0
