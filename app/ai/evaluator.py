from typing import List

BOARD_SIZE = 15
EMPTY = 0

# TrÃ¡Â»Âng sÃ¡Â»â€˜ Heuristic
SCORE_FIVE = 100_000_000
SCORE_OPEN_FOUR = 10_000_000
SCORE_BLOCKED_FOUR = 500_000
SCORE_OPEN_THREE = 100_000
SCORE_BLOCKED_THREE = 5_000
SCORE_OPEN_TWO = 500
SCORE_BLOCKED_TWO = 50


def evaluate_line(line: List[int], player: int) -> int:  # noqa: C901
    """
    Ã„ÂÃƒÂ¡nh giÃƒÂ¡ Ã„â€˜iÃ¡Â»Æ’m cÃ¡Â»Â§a mÃ¡Â»â„¢t dÃƒÂ£y ÃƒÂ´ (chuÃ¡Â»â€”i 1D) theo cÃƒÂ¡c pattern cÃ¡Â»Â Caro.
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

    # 1. ChuÃ¡Â»â€”i 5 quÃƒÂ¢n
    if "PPPPP" in s:
        return SCORE_FIVE

    # 2. 4 quÃƒÂ¢n
    if "EPPPPE" in s:
        score += SCORE_OPEN_FOUR
    if "OPPPPE" in s or "EPPPPO" in s:
        score += SCORE_BLOCKED_FOUR
    if "PPPEP" in s or "PEPPP" in s or "PPEPP" in s:
        score += SCORE_BLOCKED_FOUR

    # 3. 3 quÃƒÂ¢n
    if "EPPPE" in s or "EPEPPE" in s or "EPPEPE" in s:
        score += SCORE_OPEN_THREE
    if "OPPPE" in s or "EPPPO" in s:
        score += SCORE_BLOCKED_THREE

    # 4. 2 quÃƒÂ¢n
    if "EEPPEE" in s or "EEPEPE" in s:
        score += SCORE_OPEN_TWO
    elif "OPPE" in s or "EPPO" in s:
        score += SCORE_BLOCKED_TWO

    return score


def evaluate_board(board: List[List[int]], ai_player: int, human_player: int) -> int:
    """
    QuÃƒÂ©t toÃƒÂ n bÃ¡Â»â„¢ bÃƒÂ n cÃ¡Â»Â theo 4 hÃ†Â°Ã¡Â»â€ºng vÃƒÂ  tÃƒÂ­nh tÃ¡Â»â€¢ng Ã„â€˜iÃ¡Â»Æ’m heuristic.
    """
    ai_score = 0
    human_score = 0

    # 1. HÃƒÂ ng ngang
    for r in range(BOARD_SIZE):
        line = board[r]
        ai_score += evaluate_line(line, ai_player)
        human_score += evaluate_line(line, human_player)

    # 2. HÃƒÂ ng dÃ¡Â»Âc
    for c in range(BOARD_SIZE):
        line = [board[r][c] for r in range(BOARD_SIZE)]
        ai_score += evaluate_line(line, ai_player)
        human_score += evaluate_line(line, human_player)

    # 3. Ã„ÂÃ†Â°Ã¡Â»Âng chÃƒÂ©o chÃƒÂ­nh (\)
    for k in range(-BOARD_SIZE + 1, BOARD_SIZE):
        line = [board[r][r - k] for r in range(BOARD_SIZE) if 0 <= r - k < BOARD_SIZE]
        if len(line) >= 5:
            ai_score += evaluate_line(line, ai_player)
            human_score += evaluate_line(line, human_player)

    # 4. Ã„ÂÃ†Â°Ã¡Â»Âng chÃƒÂ©o phÃ¡Â»Â¥ (/)
    for k in range(BOARD_SIZE * 2 - 1):
        line = [board[r][k - r] for r in range(BOARD_SIZE) if 0 <= k - r < BOARD_SIZE]
        if len(line) >= 5:
            ai_score += evaluate_line(line, ai_player)
            human_score += evaluate_line(line, human_player)

    return int(ai_score - 1.2 * human_score)
