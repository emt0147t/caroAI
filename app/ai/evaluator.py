from typing import List

BOARD_SIZE = 15
EMPTY = 0

# Trá»ng sá»‘ Heuristic
SCORE_FIVE = 100_000_000
SCORE_OPEN_FOUR = 10_000_000
SCORE_BLOCKED_FOUR = 500_000
SCORE_OPEN_THREE = 100_000
SCORE_BLOCKED_THREE = 5_000
SCORE_OPEN_TWO = 500
SCORE_BLOCKED_TWO = 50


def evaluate_line(line: List[int], player: int) -> int:  # noqa: C901
    """
    ÄÃ¡nh giÃ¡ Ä‘iá»ƒm cá»§a má»™t dÃ£y Ã´ (chuá»—i 1D) theo cÃ¡c pattern cá» Caro.
    """
    if len(line) < 5:
        return 0

    score = 0
    chars = []
    for cell in line:
        if cell == player:
            chars.append('P')
        elif cell == EMPTY:
            chars.append('E')
        else:
            chars.append('O')
    s = "".join(chars)

    # 1. Chuá»—i 5 quÃ¢n
    if "PPPPP" in s:
        return SCORE_FIVE

    # 2. 4 quÃ¢n
    if "EPPPPE" in s:
        score += SCORE_OPEN_FOUR
    if "OPPPPE" in s or "EPPPPO" in s:
        score += SCORE_BLOCKED_FOUR
    if "PPPEP" in s or "PEPPP" in s or "PPEPP" in s:
        score += SCORE_BLOCKED_FOUR

    # 3. 3 quÃ¢n
    if "EPPPE" in s or "EPEPPE" in s or "EPPEPE" in s:
        score += SCORE_OPEN_THREE
    if "OPPPE" in s or "EPPPO" in s:
        score += SCORE_BLOCKED_THREE

    # 4. 2 quÃ¢n
    if "EEPPEE" in s or "EEPEPE" in s:
        score += SCORE_OPEN_TWO
    elif "OPPE" in s or "EPPO" in s:
        score += SCORE_BLOCKED_TWO

    return score


def evaluate_board(board: List[List[int]], ai_player: int, human_player: int) -> int:
    """
    QuÃ©t toÃ n bá»™ bÃ n cá» theo 4 hÆ°á»›ng vÃ  tÃ­nh tá»•ng Ä‘iá»ƒm heuristic.
    """
    ai_score = 0
    human_score = 0

    # 1. HÃ ng ngang
    for r in range(BOARD_SIZE):
        line = board[r]
        ai_score += evaluate_line(line, ai_player)
        human_score += evaluate_line(line, human_player)

    # 2. HÃ ng dá»c
    for c in range(BOARD_SIZE):
        line = [board[r][c] for r in range(BOARD_SIZE)]
        ai_score += evaluate_line(line, ai_player)
        human_score += evaluate_line(line, human_player)

    # 3. ÄÆ°á»ng chÃ©o chÃ­nh (\\)
    for k in range(-BOARD_SIZE + 1, BOARD_SIZE):
        line = [board[r][r - k] for r in range(BOARD_SIZE) if 0 <= r - k < BOARD_SIZE]
        if len(line) >= 5:
            ai_score += evaluate_line(line, ai_player)
            human_score += evaluate_line(line, human_player)

    # 4. ÄÆ°á»ng chÃ©o phá»¥ (/)
    for k in range(BOARD_SIZE * 2 - 1):
        line = [board[r][k - r] for r in range(BOARD_SIZE) if 0 <= k - r < BOARD_SIZE]
        if len(line) >= 5:
            ai_score += evaluate_line(line, ai_player)
            human_score += evaluate_line(line, human_player)

    return int(ai_score - 1.2 * human_score)
