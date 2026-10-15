from app.ai.engine import get_ai_move

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def create_empty_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def test_engine_output_contract():
    """Output pháº£i Ä‘Ãºng Ä‘á»‹nh dáº¡ng dict gá»“m row, col, score, elapsed_ms."""
    board = create_empty_board()
    board[7][7] = PLAYER_X

    result = get_ai_move(board, ai_player=PLAYER_O, difficulty="MEDIUM")

    assert "row" in result
    assert "col" in result
    assert "score" in result
    assert "elapsed_ms" in result
    assert 0 <= result["row"] < BOARD_SIZE
    assert 0 <= result["col"] < BOARD_SIZE
    assert isinstance(result["elapsed_ms"], float)
    assert result["elapsed_ms"] >= 0


def test_engine_handles_different_difficulties():
    """AI Engine pháº£i xá»­ lÃ½ mÆ°á»£t mÃ  cáº£ 3 má»©c Ä‘á»™ EASY, MEDIUM, HARD."""
    board = create_empty_board()
    board[7][7] = PLAYER_X

    for diff in ["EASY", "MEDIUM", "HARD"]:
        res = get_ai_move(board, ai_player=PLAYER_O, difficulty=diff)
        assert res["row"] is not None
        assert res["col"] is not None
