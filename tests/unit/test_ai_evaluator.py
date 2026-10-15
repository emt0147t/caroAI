from app.ai.evaluator import evaluate_board, evaluate_line

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def test_five_in_a_row_score():
    """Chuá»—i 5 quÃ¢n liÃªn tiáº¿p pháº£i cÃ³ Ä‘iá»ƒm sá»‘ chiáº¿n tháº¯ng cá»±c lá»›n."""
    line = [PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O]
    score = evaluate_line(line, player=PLAYER_O)
    assert score >= 100_000_000


def test_open_four_score_higher_than_open_three():
    """4 quÃ¢n má»Ÿ 2 Ä‘áº§u (.XXXX.) pháº£i cÃ³ Ä‘iá»ƒm cao hÆ¡n nhiá»u so vá»›i 3 quÃ¢n má»Ÿ (.XXX.)."""
    open_four = [EMPTY, PLAYER_O, PLAYER_O, PLAYER_O, PLAYER_O, EMPTY]
    open_three = [EMPTY, PLAYER_O, PLAYER_O, PLAYER_O, EMPTY]

    score_four = evaluate_line(open_four, player=PLAYER_O)
    score_three = evaluate_line(open_three, player=PLAYER_O)

    assert score_four > score_three * 10


def test_evaluate_board_favors_winning_player():
    """BÃ n cá» cÃ³ tháº¿ cá» máº¡nh cá»§a AI (PLAYER_O) pháº£i cÃ³ Ä‘iá»ƒm dÆ°Æ¡ng lá»›n."""
    board = create_empty_board()
    for c in range(5, 9):
        board[7][c] = PLAYER_O

    score = evaluate_board(board, ai_player=PLAYER_O, human_player=PLAYER_X)
    assert score > 0
