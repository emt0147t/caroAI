from typing import List, Tuple, Optional
from app.ai.evaluator import evaluate_board, SCORE_FIVE
from app.ai.move_generator import get_candidate_moves

BOARD_SIZE = 15
EMPTY = 0
INF = 1_000_000_000


def minimax(  # noqa: C901
    board: List[List[int]],
    depth: int,
    alpha: int,
    beta: int,
    is_maximizing: bool,
    ai_player: int,
    human_player: int,
    candidate_limit: int = 12
) -> Tuple[Optional[Tuple[int, int]], int]:
    """
    DuyÃ¡Â»â€¡t cÃƒÂ¢y Minimax vÃ¡Â»â€ºi cÃ¡ÂºÂ¯t tÃ¡Â»â€°a Alpha-Beta vÃƒÂ  Backtracking.
    """
    candidates = get_candidate_moves(board, radius=2)
    if not candidates:
        return ((7, 7), 0)

    # 1. KiÃ¡Â»Æ’m tra Ã„â€˜iÃ¡Â»Âu kiÃ¡Â»â€¡n thÃ¡ÂºÂ¯ng / thua ngay lÃ¡ÂºÂ­p tÃ¡Â»Â©c
    for r, c in candidates:
        board[r][c] = ai_player
        score = evaluate_board(board, ai_player, human_player)
        board[r][c] = EMPTY
        if score >= SCORE_FIVE:
            return ((r, c), SCORE_FIVE)

        board[r][c] = human_player
        score_opp = evaluate_board(board, human_player, ai_player)
        board[r][c] = EMPTY
        if score_opp >= SCORE_FIVE:
            if not is_maximizing:
                return ((r, c), -SCORE_FIVE)

    if depth == 0:
        return (None, evaluate_board(board, ai_player, human_player))

    # 2. SÃ¡ÂºÂ¯p xÃ¡ÂºÂ¿p sÃ†Â¡ bÃ¡Â»â„¢ cÃƒÂ¡c nÃ†Â°Ã¡Â»â€ºc Ã„â€˜i (Move Ordering) Ã„â€˜Ã¡Â»Æ’ tÃ„Æ’ng hiÃ¡Â»â€¡u quÃ¡ÂºÂ£ Alpha-Beta  # noqa: E501
    scored_candidates = []
    current_player = ai_player if is_maximizing else human_player
    for r, c in candidates:
        board[r][c] = current_player
        s = evaluate_board(board, ai_player, human_player)
        board[r][c] = EMPTY
        scored_candidates.append(((r, c), s))

    scored_candidates.sort(key=lambda item: item[1], reverse=is_maximizing)
    limited_candidates = [m for m, _ in scored_candidates[:candidate_limit]]

    # 3. DuyÃ¡Â»â€¡t Minimax
    best_move = None

    if is_maximizing:
        max_eval = -INF
        for r, c in limited_candidates:
            board[r][c] = ai_player
            _, evaluation = minimax(board, depth - 1, alpha, beta, False, ai_player, human_player, candidate_limit)
            board[r][c] = EMPTY

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = (r, c)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return (best_move, max_eval)
    else:
        min_eval = INF
        for r, c in limited_candidates:
            board[r][c] = human_player
            _, evaluation = minimax(board, depth - 1, alpha, beta, True, ai_player, human_player, candidate_limit)
            board[r][c] = EMPTY

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = (r, c)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return (best_move, min_eval)


def find_best_move(
    board: List[List[int]],
    ai_player: int,
    depth: int = 2,
    candidate_limit: int = 12
) -> Tuple[Tuple[int, int], int]:
    """
    Entry point tÃƒÂ¬m nÃ†Â°Ã¡Â»â€ºc Ã„â€˜i tÃ¡Â»â€˜i Ã†Â°u cho AI.
    """
    human_player = 2 if ai_player == 1 else 1

    # KiÃ¡Â»Æ’m tra chÃ¡ÂºÂ·n Ã„â€˜e dÃ¡Â»Âa trÃ¡Â»Â±c tiÃ¡ÂºÂ¿p trÃ†Â°Ã¡Â»â€ºc khi duyÃ¡Â»â€¡t cÃƒÂ¢y sÃƒÂ¢u
    candidates = get_candidate_moves(board, radius=2)
    if not candidates:
        return ((7, 7), 0)

    # ChÃ¡ÂºÂ·n ngay nÃ¡ÂºÂ¿u Ã„â€˜Ã¡Â»â€˜i thÃ¡Â»Â§ cÃƒÂ³ nÃ†Â°Ã¡Â»â€ºc tÃ¡ÂºÂ¡o chuÃ¡Â»â€”i 5
    for r, c in candidates:
        board[r][c] = human_player
        score_opp = evaluate_board(board, human_player, ai_player)
        board[r][c] = EMPTY
        if score_opp >= SCORE_FIVE:
            return ((r, c), -score_opp)

    best_move, score = minimax(
        board,
        depth=depth,
        alpha=-INF,
        beta=INF,
        is_maximizing=True,
        ai_player=ai_player,
        human_player=human_player,
        candidate_limit=candidate_limit
    )

    if best_move is None and candidates:
        best_move = candidates[0]

    return (best_move, score)
