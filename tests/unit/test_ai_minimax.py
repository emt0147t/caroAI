from app.ai.minimax import find_best_move

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def test_minimax_takes_immediate_win():
    """AI (PLAYER_O) pháº£i Ä‘i ngay vÃ o Ã´ káº¿t thÃºc Ä‘á»ƒ táº¡o chuá»—i 5 quÃ¢n tháº¯ng cuá»™c."""
    board = create_empty_board()
    # O Ä‘Ã£ cÃ³ 4 quÃ¢n: (7, 3), (7, 4), (7, 5), (7, 6). Ã” (7, 7) Ä‘ang trá»‘ng
    for c in range(3, 7):
        board[7][c] = PLAYER_O

    best_move, score = find_best_move(board, ai_player=PLAYER_O, depth=2)
    assert best_move == (7, 7) or best_move == (7, 2)


def test_minimax_blocks_opponent_four():
    """AI (PLAYER_O) pháº£i cháº·n ngay khi Ä‘á»‘i thá»§ X Ä‘Ã£ cÃ³ 4 quÃ¢n nguy hiá»ƒm."""
    board = create_empty_board()
    # Äá»‘i thá»§ X cÃ³ 4 quÃ¢n: (7, 3), (7, 4), (7, 5), (7, 6)
    for c in range(3, 7):
        board[7][c] = PLAYER_X
    # AI cÃ³ 1 quÃ¢n rá»i ráº¡c á»Ÿ chá»— khÃ¡c
    board[0][0] = PLAYER_O

    best_move, score = find_best_move(board, ai_player=PLAYER_O, depth=2)
    # AI buá»™c pháº£i Ä‘i vÃ o 1 trong 2 Ä‘áº§u (7, 2) hoáº·c (7, 7) Ä‘á»ƒ cháº·n
    assert best_move in [(7, 2), (7, 7)]
