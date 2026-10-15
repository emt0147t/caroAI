from app.ai.move_generator import get_candidate_moves

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def test_empty_board_returns_center():
    """Náº¿u bÃ n cá» trá»‘ng hoÃ n toÃ n, AI pháº£i chá»n Ã´ trung tÃ¢m (7, 7)."""
    board = create_empty_board()
    candidates = get_candidate_moves(board)
    assert candidates == [(7, 7)]


def test_candidates_around_single_stone():
    """Náº¿u chá»‰ cÃ³ 1 quÃ¢n cá» táº¡i (7, 7), cÃ¡c candidate chá»‰ náº±m trong bÃ¡n kÃ­nh lÃ¢n cáº­n."""
    board = create_empty_board()
    board[7][7] = PLAYER_X
    candidates = get_candidate_moves(board, radius=1)

    # 8 Ã´ xung quanh (7,7)
    expected = {
        (6, 6), (6, 7), (6, 8),
        (7, 6),         (7, 8),
        (8, 6), (8, 7), (8, 8)
    }
    assert set(candidates) == expected
    assert (7, 7) not in candidates  # Ã” Ä‘Ã£ cÃ³ quÃ¢n khÃ´ng Ä‘Æ°á»£c lÃ  candidate


def test_no_out_of_bounds_candidates():
    """QuÃ¢n cá» náº±m á»Ÿ gÃ³c (0, 0) khÃ´ng Ä‘Æ°á»£c sinh candidate cÃ³ tá»a Ä‘á»™ Ã¢m."""
    board = create_empty_board()
    board[0][0] = PLAYER_X
    candidates = get_candidate_moves(board, radius=1)

    expected = {(0, 1), (1, 0), (1, 1)}
    assert set(candidates) == expected
