"""Time-bounded, threat-aware search for the stronger Caro AI levels.

The legacy minimax entry points remain available for existing regression tests.
This module is the production search path for HARD and IMPOSSIBLE.
"""
from dataclasses import dataclass, field
from functools import lru_cache
from random import choice
from time import perf_counter
from typing import Dict, List, Optional, Tuple

from app.ai.evaluator import (
    BOARD_SIZE,
    EMPTY,
    SCORE_FIVE,
    _ALL_NON_ROW_COORDS,
    check_win_at,
    get_board_raw_scores,
    get_cell_lines_scores,
)
from app.ai.move_generator import get_candidate_moves
from app.ai.search_stats import SearchStats

Move = Tuple[int, int]
MATE_SCORE = 10_000_000_000
INF = 20_000_000_000
EXACT, LOWER_BOUND, UPPER_BOUND = 0, 1, 2


class SearchTimeout(Exception):
    """Raised internally when the time or node budget is exhausted."""


@dataclass
class TTEntry:
    depth: int
    score: int
    bound: int
    best_move: Optional[Move]


@dataclass
class SearchContext:
    deadline: float
    node_budget: int
    stats: Optional[SearchStats] = None
    nodes: int = 0
    work: int = 0
    tt_hits: int = 0
    cutoffs: int = 0
    table: Dict[bytes, TTEntry] = field(default_factory=dict)

    def visit(self) -> None:
        self.nodes += 1
        if self.stats is not None:
            self.stats.nodes = self.nodes
        if self.nodes > self.node_budget or perf_counter() >= self.deadline:
            raise SearchTimeout

    def check_work(self) -> None:
        self.work += 1
        if (self.work & 31) == 0:
            if self.stats is not None:
                self.stats.check_deadline()
            if self.nodes >= self.node_budget or perf_counter() >= self.deadline:
                raise SearchTimeout


def _board_key(board: List[List[int]]) -> bytes:
    return bytes(cell for row in board for cell in row)


@lru_cache(maxsize=32768)
def _threat_features(board_key: bytes, player: int):
    """Return unique next-move wins, open threes, and broken threes.

    A winning cell is any empty cell that completes a contiguous five-cell
    window containing four stones of this player and no opponent stone.
    """
    opponent = 2 if player == 1 else 1
    lines = []
    for row in range(BOARD_SIZE):
        start = row * BOARD_SIZE
        lines.append((
            tuple((row, col) for col in range(BOARD_SIZE)),
            board_key[start:start + BOARD_SIZE],
        ))
    for coords in _ALL_NON_ROW_COORDS:
        values = bytes(board_key[row * BOARD_SIZE + col] for row, col in coords)
        lines.append((coords, values))

    winning_cells = set()
    open_three_shapes = set()
    broken_three_shapes = set()

    for coords, values in lines:
        for start in range(len(values) - 4):
            window = values[start:start + 5]
            if opponent in window:
                continue
            own = [idx for idx, value in enumerate(window) if value == player]
            empty = [idx for idx, value in enumerate(window) if value == EMPTY]

            if len(own) == 4 and len(empty) == 1:
                winning_cells.add(coords[start + empty[0]])
            elif len(own) == 3 and len(empty) == 2:
                shape = tuple(coords[start + idx] for idx in own)
                if own == [1, 2, 3]:
                    open_three_shapes.add(shape)
                elif own[-1] - own[0] <= 3:
                    broken_three_shapes.add(shape)

    return tuple(sorted(winning_cells)), len(open_three_shapes), len(broken_three_shapes)


def _threat_value(features) -> int:
    wins, open_threes, broken_threes = features
    value = 0
    if len(wins) >= 2:
        # Two separate winning cells form a fork that cannot be blocked in one move.
        value += 55_000_000 + min(len(wins) - 2, 4) * 5_000_000
    elif len(wins) == 1:
        value += 9_000_000
    value += min(open_threes, 4) * 220_000
    if open_threes >= 2:
        value += 1_200_000
    value += min(broken_threes, 4) * 55_000
    return value


def _position_score(
    board_key: bytes,
    p1_score: int,
    p2_score: int,
    ai_player: int,
) -> int:
    """AI-perspective evaluation with a slight initiative bias.

    Immediate four threats and multi-line open-three forks are scored separately
    from the legacy pattern total so attack creation is not undervalued as mere
    material to block.
    """
    if ai_player == 1:
        ai_raw, human_raw = p1_score, p2_score
        human_player = 2
    else:
        ai_raw, human_raw = p2_score, p1_score
        human_player = 1

    ai_features = _threat_features(board_key, ai_player)
    human_features = _threat_features(board_key, human_player)
    return int(
        ai_raw * 1.05
        - human_raw
        + _threat_value(ai_features)
        - _threat_value(human_features)
    )


def _rank_moves(
    board: List[List[int]],
    player: int,
    ai_player: int,
    p1_score: int,
    p2_score: int,
    candidate_limit: int,
    tt_move: Optional[Move],
    context: SearchContext,
    forced_move: Optional[Move] = None,
):
    candidates = [forced_move] if forced_move is not None else get_candidate_moves(board, radius=1)
    ranked = []
    maximizing_for_ai = player == ai_player

    for row, col in candidates:
        context.check_work()
        if board[row][col] != EMPTY:
            continue

        old_p1, old_p2 = get_cell_lines_scores(board, row, col)
        board[row][col] = player
        try:
            new_p1, new_p2 = get_cell_lines_scores(board, row, col)
        finally:
            board[row][col] = EMPTY

        next_p1 = p1_score - old_p1 + new_p1
        next_p2 = p2_score - old_p2 + new_p2
        ai_after = next_p1 if ai_player == 1 else next_p2
        human_after = next_p2 if ai_player == 1 else next_p1

        # A small initiative term favours creating our own patterns. Forced
        # tactical blocks are handled separately and therefore remain mandatory.
        own_delta = (new_p1 - old_p1) if player == 1 else (new_p2 - old_p2)
        opponent_delta = (new_p2 - old_p2) if player == 1 else (new_p1 - old_p1)
        initiative = own_delta * 0.10 - opponent_delta * 0.05

        ai_utility = ai_after * 1.05 - human_after
        side_utility = ai_utility if maximizing_for_ai else -ai_utility
        center_distance = abs(row - BOARD_SIZE // 2) + abs(col - BOARD_SIZE // 2)
        center_bonus = max(0, 8 - center_distance) * 25
        order_score = side_utility + initiative + center_bonus

        ranked.append((order_score, (row, col), next_p1, next_p2))

    ranked.sort(
        key=lambda item: (
            item[1] == tt_move,
            item[0],
            -abs(item[1][0] - BOARD_SIZE // 2) - abs(item[1][1] - BOARD_SIZE // 2),
            -item[1][0],
            -item[1][1],
        ),
        reverse=True,
    )
    limited = ranked[:candidate_limit]
    if context.stats is not None:
        context.stats.candidate_cap_considered += len(ranked)
        context.stats.candidate_cap_pruned += max(0, len(ranked) - len(limited))
        context.stats.record_branching_factor(len(limited))
    return limited


def _minimax_search(  # noqa: C901
    board: List[List[int]],
    depth: int,
    alpha: int,
    beta: int,
    player: int,
    ai_player: int,
    p1_score: int,
    p2_score: int,
    candidate_limit: int,
    ply: int,
    extensions: int,
    context: SearchContext,
) -> int:
    context.visit()
    opponent = 2 if player == 1 else 1
    key = _board_key(board)
    tt_key = key + bytes((player,))

    # If the side to move can win now, do not waste time exploring alternatives.
    own_features = _threat_features(key, player)
    if own_features[0]:
        if context.stats is not None:
            context.stats.leaves += 1
        return MATE_SCORE - ply if player == ai_player else -MATE_SCORE + ply

    opponent_features = _threat_features(key, opponent)
    opponent_wins = opponent_features[0]
    if len(opponent_wins) >= 2:
        # There are two distinct immediate winning cells; one move cannot block both.
        if context.stats is not None:
            context.stats.leaves += 1
        return MATE_SCORE - ply if opponent == ai_player else -MATE_SCORE + ply

    # A single immediate threat must be answered even at the nominal horizon.
    forced_move = opponent_wins[0] if len(opponent_wins) == 1 else None
    if depth <= 0:
        own_open_threes = own_features[1]
        opponent_open_threes = opponent_features[1]
        if extensions >= 1 or not (forced_move or own_open_threes >= 2 or opponent_open_threes >= 2):
            return _position_score(key, p1_score, p2_score, ai_player)
        depth = 1
        extensions += 1

    alpha_original, beta_original = alpha, beta
    entry = context.table.get(tt_key)
    tt_move = None
    if entry is not None:
        tt_move = entry.best_move
        if entry.depth >= depth:
            context.tt_hits += 1
            if context.stats is not None and entry.bound == EXACT:
                context.stats.leaves += 1
            if entry.bound == EXACT:
                return entry.score
            if entry.bound == LOWER_BOUND:
                alpha = max(alpha, entry.score)
            elif entry.bound == UPPER_BOUND:
                beta = min(beta, entry.score)
            if alpha >= beta:
                return entry.score

    ranked = _rank_moves(
        board=board,
        player=player,
        ai_player=ai_player,
        p1_score=p1_score,
        p2_score=p2_score,
        candidate_limit=candidate_limit,
        tt_move=tt_move,
        context=context,
        forced_move=forced_move,
    )
    if not ranked:
        if context.stats is not None:
            context.stats.leaves += 1
        return _position_score(key, p1_score, p2_score, ai_player)

    maximizing = player == ai_player
    best_score = -INF if maximizing else INF
    best_move = None

    for index, (_, move, next_p1, next_p2) in enumerate(ranked):
        context.check_work()
        if context.stats is not None:
            context.stats.expanded_candidates += 1
        row, col = move
        board[row][col] = player
        try:
            if check_win_at(board, row, col, player):
                score = MATE_SCORE - (ply + 1) if player == ai_player else -MATE_SCORE + (ply + 1)
            else:
                score = _minimax_search(
                    board=board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    player=opponent,
                    ai_player=ai_player,
                    p1_score=next_p1,
                    p2_score=next_p2,
                    candidate_limit=candidate_limit,
                    ply=ply + 1,
                    extensions=extensions,
                    context=context,
                )
        finally:
            board[row][col] = EMPTY

        if maximizing:
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, best_score)
        else:
            if score < best_score:
                best_score, best_move = score, move
            beta = min(beta, best_score)

        if beta <= alpha:
            context.cutoffs += 1
            if context.stats is not None:
                context.stats.alpha_beta_cutoffs += 1
                context.stats.alpha_beta_pruned += max(0, len(ranked) - index - 1)
            break

    if best_move is not None:
        if best_score <= alpha_original:
            bound = UPPER_BOUND
        elif best_score >= beta_original:
            bound = LOWER_BOUND
        else:
            bound = EXACT
        if len(context.table) >= 50000:
            context.table.clear()
        context.table[tt_key] = TTEntry(depth, best_score, bound, best_move)

    return best_score


def _root_search(
    board: List[List[int]],
    depth: int,
    ai_player: int,
    p1_score: int,
    p2_score: int,
    candidate_limit: int,
    context: SearchContext,
):
    key = _board_key(board)
    ai_wins = _threat_features(key, ai_player)[0]
    if ai_wins:
        return [(MATE_SCORE, ai_wins[0])]

    human_player = 2 if ai_player == 1 else 1
    human_wins = _threat_features(key, human_player)[0]
    forced_move = human_wins[0] if len(human_wins) == 1 else None

    root_key = key + bytes((ai_player,))
    old_entry = context.table.get(root_key)
    tt_move = old_entry.best_move if old_entry else None

    ranked = _rank_moves(
        board=board,
        player=ai_player,
        ai_player=ai_player,
        p1_score=p1_score,
        p2_score=p2_score,
        candidate_limit=candidate_limit,
        tt_move=tt_move,
        context=context,
        forced_move=forced_move,
    )
    scores = []
    for _, move, next_p1, next_p2 in ranked:
        context.check_work()
        row, col = move
        board[row][col] = ai_player
        try:
            if check_win_at(board, row, col, ai_player):
                score = MATE_SCORE - 1
            else:
                score = _minimax_search(
                    board=board,
                    depth=depth - 1,
                    alpha=-INF,
                    beta=INF,
                    player=human_player,
                    ai_player=ai_player,
                    p1_score=next_p1,
                    p2_score=next_p2,
                    candidate_limit=candidate_limit,
                    ply=1,
                    extensions=0,
                    context=context,
                )
        finally:
            board[row][col] = EMPTY
        scores.append((score, move))

    if scores:
        best_score = max(score for score, _ in scores)
        best_moves = [move for score, move in scores if score == best_score]
        if len(context.table) >= 50000:
            context.table.clear()
        context.table[root_key] = TTEntry(depth, best_score, EXACT, best_moves[0])
    return scores


def find_strategic_move(  # noqa: C901
    board: List[List[int]],
    ai_player: int,
    *,
    max_depth: int,
    candidate_limit: int,
    time_budget_ms: int,
    node_budget: int,
    diversify: bool = False,
    stats: Optional[SearchStats] = None,
):
    """Find a strong move with iterative deepening and hard time/node budgets.

    A deterministic legal fallback is selected before search starts. Each depth
    iteration is completed atomically: if a later iteration times out, the
    best move from the last completed depth (or fallback) is returned.
    """
    if ai_player not in (1, 2):
        raise ValueError("ai_player must be 1 or 2")
    human_player = 2 if ai_player == 1 else 1
    candidates = get_candidate_moves(board, radius=1)
    if not candidates:
        raise ValueError("No legal candidate moves available for this board")

    start = perf_counter()
    key = _board_key(board)
    if stats is not None:
        stats.root_candidates = len(candidates)

    # Mandatory tactical checks finish before the optional search clock starts.
    ai_wins = _threat_features(key, ai_player)[0]
    if ai_wins:
        if stats is not None:
            stats.shortcut = "immediate_win"
            stats.elapsed_ms = (perf_counter() - start) * 1000.0
        return ai_wins[0], SCORE_FIVE, {"depth": 0, "nodes": 0, "tt_hits": 0}

    human_wins = _threat_features(key, human_player)[0]
    if len(human_wins) == 1:
        if stats is not None:
            stats.shortcut = "forced_block"
            stats.elapsed_ms = (perf_counter() - start) * 1000.0
        return human_wins[0], -SCORE_FIVE, {"depth": 0, "nodes": 0, "tt_hits": 0}

    best_move = min(
        candidates,
        key=lambda move: (
            abs(move[0] - BOARD_SIZE // 2) + abs(move[1] - BOARD_SIZE // 2),
            move[0],
            move[1],
        ),
    )
    p1_score, p2_score = get_board_raw_scores(board)
    best_score = _position_score(key, p1_score, p2_score, ai_player)
    completed_depth = 0

    context = SearchContext(
        deadline=perf_counter() + max(0, time_budget_ms) / 1000.0,
        node_budget=max(1, node_budget),
        stats=stats,
    )
    if stats is not None:
        stats.shortcut = "none"

    for depth in range(1, max_depth + 1):
        try:
            scores = _root_search(
                board=board,
                depth=depth,
                ai_player=ai_player,
                p1_score=p1_score,
                p2_score=p2_score,
                candidate_limit=candidate_limit,
                context=context,
            )
        except SearchTimeout:
            if stats is not None:
                stats.timed_out = True
            break

        if not scores:
            break
        iteration_best = max(score for score, _ in scores)
        choices = [move for score, move in scores if score == iteration_best]
        best_score = iteration_best
        best_move = choice(choices) if diversify and len(choices) > 1 else choices[0]
        completed_depth = depth

        if abs(best_score) >= MATE_SCORE - 100:
            break

    elapsed_ms = (perf_counter() - start) * 1000.0
    if stats is not None:
        stats.elapsed_ms = elapsed_ms
        stats.nodes = context.nodes

    search_info = {
        "depth": completed_depth,
        "nodes": context.nodes,
        "tt_hits": context.tt_hits,
        "cutoffs": context.cutoffs,
        "elapsed_ms": round(elapsed_ms, 2),
        "transposition_table_size": len(context.table),
    }
    return best_move, int(best_score), search_info
