from typing import List, Tuple, Optional
from app.ai.evaluator import (
    SCORE_FIVE,
    get_board_raw_scores,
    get_cell_lines_scores,
    check_win_at,
    has_five_in_a_row,
)
from app.ai.move_generator import get_candidate_moves
from app.ai.search_stats import SearchStats, SearchTimeBudgetExceeded

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
    candidate_limit: int = 12,
    stats: SearchStats | None = None,
) -> Tuple[Optional[Tuple[int, int]], int]:
    """
    Duyệt cây Minimax với cắt tỉa Alpha-Beta và Backtracking.
    Sử dụng Incremental 4-Line Delta evaluation để đạt tốc độ tối đa.
    """
    if stats is not None:
        stats.check_deadline()
        stats.nodes += 1

    candidates = get_candidate_moves(board, radius=2)
    if stats is not None:
        stats.generated_candidates += len(candidates)
    if not candidates:
        if stats is not None:
            stats.leaves += 1
        return ((7, 7), 0)

    # 1. Kiểm tra trạng thái thắng/thua đã có sẵn trên bàn cờ (xác định bằng 5 quân thực tế)
    if has_five_in_a_row(board, ai_player):
        if stats is not None:
            stats.leaves += 1
        return (None, SCORE_FIVE)
    if has_five_in_a_row(board, human_player):
        if stats is not None:
            stats.leaves += 1
        return (None, -SCORE_FIVE)

    base_p1, base_p2 = get_board_raw_scores(board)
    base_ai, base_hu = (base_p1, base_p2) if ai_player == 1 else (base_p2, base_p1)

    # 2. Kiểm tra tactical và tính điểm move ordering cho lượt của current_player
    scored_candidates = []
    current_player = ai_player if is_maximizing else human_player

    for r, c in candidates:
        if stats is not None:
            stats.check_deadline()
        old_p1, old_p2 = get_cell_lines_scores(board, r, c)
        old_ai, old_hu = (old_p1, old_p2) if ai_player == 1 else (old_p2, old_p1)

        board[r][c] = current_player
        if is_maximizing:
            # AI có nước tạo chuỗi 5 ngay lập tức
            if check_win_at(board, r, c, ai_player):
                board[r][c] = EMPTY
                return ((r, c), SCORE_FIVE)
        else:
            # Human có nước tạo chuỗi 5 ngay lập tức trong lượt của mình
            if check_win_at(board, r, c, human_player):
                board[r][c] = EMPTY
                return ((r, c), -SCORE_FIVE)

        new_p1, new_p2 = get_cell_lines_scores(board, r, c)
        board[r][c] = EMPTY
        new_ai, new_hu = (new_p1, new_p2) if ai_player == 1 else (new_p2, new_p1)

        ai_total = base_ai - old_ai + new_ai
        hu_total = base_hu - old_hu + new_hu
        score = int(ai_total - 1.2 * hu_total)
        scored_candidates.append(((r, c), score))

    if depth == 0:
        if stats is not None:
            stats.leaves += 1
        return (None, int(base_ai - 1.2 * base_hu))

    # 3. Sắp xếp sơ bộ các nước đi (Move Ordering) để tăng hiệu quả Alpha-Beta
    # Deterministic tie-breaking improves alpha-beta move ordering and makes
    # equal-score searches reproducible across Python hash seeds.
    def move_order_key(item):
        (r, c), score = item
        score_key = -score if is_maximizing else score
        center_distance = abs(r - BOARD_SIZE // 2) + abs(c - BOARD_SIZE // 2)
        return (score_key, center_distance, r, c)

    scored_candidates.sort(key=move_order_key)
    limited_candidates = [m for m, _ in scored_candidates[:candidate_limit]]
    if stats is not None:
        stats.candidate_cap_pruned += max(0, len(scored_candidates) - len(limited_candidates))
        stats.record_branching_factor(len(limited_candidates))

    # 4. Duyệt Minimax
    best_move = None

    if is_maximizing:
        max_eval = -INF
        for index, (r, c) in enumerate(limited_candidates):
            if stats is not None:
                stats.check_deadline()
                stats.expanded_candidates += 1
            board[r][c] = ai_player
            try:
                _, evaluation = minimax(
                    board, depth - 1, alpha, beta, False,
                    ai_player, human_player, candidate_limit, stats
                )
            finally:
                board[r][c] = EMPTY

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = (r, c)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                if stats is not None:
                    stats.alpha_beta_cutoffs += 1
                    stats.alpha_beta_pruned += len(limited_candidates) - index - 1
                break
        return (best_move, max_eval)
    else:
        min_eval = INF
        for index, (r, c) in enumerate(limited_candidates):
            if stats is not None:
                stats.check_deadline()
                stats.expanded_candidates += 1
            board[r][c] = human_player
            try:
                _, evaluation = minimax(
                    board, depth - 1, alpha, beta, True,
                    ai_player, human_player, candidate_limit, stats
                )
            finally:
                board[r][c] = EMPTY

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = (r, c)
            beta = min(beta, evaluation)
            if beta <= alpha:
                if stats is not None:
                    stats.alpha_beta_cutoffs += 1
                    stats.alpha_beta_pruned += len(limited_candidates) - index - 1
                break
        return (best_move, min_eval)


def find_best_move(
    board: List[List[int]],
    ai_player: int,
    depth: int = 2,
    candidate_limit: int = 12,
    stats: SearchStats | None = None,
    time_budget_ms: float | None = None,
) -> Tuple[Tuple[int, int], int]:
    """
    Entry point tìm nước đi tối ưu cho AI.
    """
    human_player = 2 if ai_player == 1 else 1

    candidates = get_candidate_moves(board, radius=2)
    if stats is not None:
        stats.root_candidates = len(candidates)
    if not candidates:
        raise ValueError("No legal candidate moves available for this board")

    # 1. Thắng ngay lập tức nếu AI có nước tạo chuỗi 5 (ưu tiên tuyệt đối)
    for r, c in candidates:
        board[r][c] = ai_player
        if check_win_at(board, r, c, ai_player):
            board[r][c] = EMPTY
            if stats is not None:
                stats.shortcut = "immediate_win"
            return ((r, c), SCORE_FIVE)
        board[r][c] = EMPTY

    # 2. Chặn ngay nếu đối thủ có nước tạo chuỗi 5 trong lượt tiếp theo
    for r, c in candidates:
        board[r][c] = human_player
        if check_win_at(board, r, c, human_player):
            board[r][c] = EMPTY
            if stats is not None:
                stats.shortcut = "forced_block"
            return ((r, c), -SCORE_FIVE)
        board[r][c] = EMPTY

    if stats is not None:
        # Mandatory root win/block scans above are never interrupted.
        stats.start_budget(time_budget_ms)

    try:
        best_move, score = minimax(
            board,
            depth=depth,
            alpha=-INF,
            beta=INF,
            is_maximizing=True,
            ai_player=ai_player,
            human_player=human_player,
            candidate_limit=candidate_limit,
            stats=stats,
        )
    except SearchTimeBudgetExceeded:
        # Return a deterministic legal move, never a partially searched illegal state.
        fallback = min(
            candidates,
            key=lambda move: (
                abs(move[0] - BOARD_SIZE // 2) + abs(move[1] - BOARD_SIZE // 2),
                move[0],
                move[1],
            ),
        )
        return (fallback, 0)

    if best_move is None and candidates:
        best_move = min(
            candidates,
            key=lambda move: (
                abs(move[0] - BOARD_SIZE // 2) + abs(move[1] - BOARD_SIZE // 2),
                move[0],
                move[1],
            ),
        )

    return (best_move, score)
