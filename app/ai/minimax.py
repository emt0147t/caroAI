from typing import List, Tuple, Optional
from app.ai.evaluator import evaluate_board, SCORE_FIVE
from app.ai.move_generator import get_candidate_moves

BOARD_SIZE = 15
EMPTY = 0
INF = 1_000_000_000

def minimax(
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
    Duyệt cây Minimax với cắt tỉa Alpha-Beta và Backtracking.
    """
    candidates = get_candidate_moves(board, radius=2)
    if not candidates:
        return ((7, 7), 0)

    # 1. Kiểm tra điều kiện thắng / thua ngay lập tức
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

    # 2. Sắp xếp sơ bộ các nước đi (Move Ordering) để tăng hiệu quả Alpha-Beta
    scored_candidates = []
    current_player = ai_player if is_maximizing else human_player
    for r, c in candidates:
        board[r][c] = current_player
        s = evaluate_board(board, ai_player, human_player)
        board[r][c] = EMPTY
        scored_candidates.append(((r, c), s))

    scored_candidates.sort(key=lambda item: item[1], reverse=is_maximizing)
    limited_candidates = [m for m, _ in scored_candidates[:candidate_limit]]

    # 3. Duyệt Minimax
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
    Entry point tìm nước đi tối ưu cho AI.
    """
    human_player = 2 if ai_player == 1 else 1

    # Kiểm tra chặn đe dọa trực tiếp trước khi duyệt cây sâu
    candidates = get_candidate_moves(board, radius=2)
    if not candidates:
        return ((7, 7), 0)

    # Chặn ngay nếu đối thủ có nước tạo chuỗi 5
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
