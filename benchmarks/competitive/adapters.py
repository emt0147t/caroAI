"""Frozen-policy baseline and independently ordered reference opponent adapters."""
from time import perf_counter

from app.ai.evaluator import get_board_raw_scores, get_cell_lines_scores
from app.ai.minimax import find_best_move
from app.ai.move_generator import get_candidate_moves
from app.ai.search_stats import SearchStats
from benchmarks.competitive.corpus import wins

BASELINE_SHA = 'b848a0e6a527b7ef3f1efa421971c356543fbc17'
BASELINE_CONFIG = {'EASY': (1, 6), 'MEDIUM': (2, 10), 'HARD': (3, 14), 'IMPOSSIBLE': (4, 20)}


def baseline(board, player, difficulty, budget_ms, seed=0):
    """Exact baseline minimax policy; explicit evaluation budget may override default."""
    started = perf_counter()
    stats = SearchStats()
    depth, cap = BASELINE_CONFIG[difficulty]
    move, score = find_best_move(board, player, depth, cap, stats, budget_ms)
    return {'row': move[0], 'col': move[1], 'score': score,
            'elapsed_ms': (perf_counter() - started) * 1000, 'search_stats': stats.to_dict()}


def candidate(board, player, difficulty, budget_ms, seed=0):
    if difficulty in ('EASY', 'MEDIUM'):
        return baseline(board, player, difficulty, budget_ms, seed)
    from app.ai.competitive import choose_move, POLICIES
    return choose_move(board, player, POLICIES[difficulty], time_budget_ms=budget_ms)


def tactical_greedy(board, player, difficulty, budget_ms, seed=0):
    """Independent domain win/block oracle plus one-ply greedy line evaluation.

    Reference has no search, no TT, no candidate bitboard threat code. It is not
    treated as a strong published external Gomoku engine.
    """
    own, enemy = wins(board, player), wins(board, 3 - player)
    if own or enemy:
        move = min(own or enemy)
    else:
        p1, p2 = get_board_raw_scores(board)
        scored = []
        for r, c in get_candidate_moves(board, radius=2):
            before1, before2 = get_cell_lines_scores(board, r, c)
            board[r][c] = player
            try:
                after1, after2 = get_cell_lines_scores(board, r, c)
            finally:
                board[r][c] = 0
            a, b = p1 - before1 + after1, p2 - before2 + after2
            value = a - 1.2 * b if player == 1 else b - 1.2 * a
            scored.append((value, -abs(r - 7) - abs(c - 7), -r, -c))
        _, _, r, c = max(scored)
        move = -r, -c
    return {'row': move[0], 'col': move[1], 'score': 0, 'elapsed_ms': 0, 'search_stats': {}}
