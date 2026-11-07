"""Deterministic tactical search with compatible TT horizons and complete timing.

HARD uses direct forcing attacks and a short threat extension. IMPOSSIBLE also
searches continuous-four proofs and a wider neighborhood. Neither is perfect play.
"""
from dataclasses import dataclass, field
import math
from time import perf_counter

from app.ai.evaluator import get_board_raw_scores, get_cell_lines_scores
from app.ai.search_stats import SearchStats
from app.ai.threats import FULL, bit, cells, encode, fork_moves, four_moves, neighborhood, winning_cells

MATE = 10_000_000_000
INF = 20_000_000_000
EXACT, LOWER, UPPER = 0, 1, 2


@dataclass(frozen=True)
class Policy:
    depth: int
    quiet_limit: int
    radius: int
    extensions: int
    proof_depth: int
    time_ms: float
    node_limit: int


POLICIES = {
    # EASY/MEDIUM definitions support policy tournaments; production stays legacy.
    'EASY': Policy(1, 6, 1, 0, 0, 40, 800),
    'MEDIUM': Policy(2, 10, 1, 0, 0, 100, 3000),
    'HARD': Policy(4, 8, 1, 1, 0, 250, 16000),
    'IMPOSSIBLE': Policy(6, 12, 2, 3, 5, 700, 40000),
}


class Exhausted(Exception):
    """Internal cooperative deadline/node stop; never escapes the engine API."""


@dataclass
class Entry:
    score: int
    bound: int
    move: tuple | None


@dataclass
class Context:
    policy: Policy
    deadline: float
    stats: SearchStats = field(default_factory=SearchStats)
    use_tt: bool = True
    table: dict = field(default_factory=dict)
    tt_probes: int = 0
    tt_hits: int = 0
    proof_nodes: int = 0
    work: int = 0

    def check(self, visit=False):
        self.work += 1
        if visit:
            self.stats.nodes += 1
        if self.stats.nodes > self.policy.node_limit or perf_counter() >= self.deadline:
            raise Exhausted

    def save(self, key, score, alpha, beta, move):
        if not self.use_tt:
            return
        bound = UPPER if score <= alpha else LOWER if score >= beta else EXACT
        if len(self.table) >= 50000:
            self.table.clear()
        self.table[key] = Entry(score, bound, move)


class Position:
    """A private copy; every apply is paired with undo in a finally block."""
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.stones = encode(board)
        self.occupied = self.stones[1] | self.stones[2]
        self.raw = get_board_raw_scores(board)

    def play(self, move, player):
        r, c = move
        assert self.board[r][c] == 0
        old = self.raw
        a, b = get_cell_lines_scores(self.board, r, c)
        self.board[r][c] = player
        x, y = get_cell_lines_scores(self.board, r, c)
        self.raw = (old[0] - a + x, old[1] - b + y)
        mark = bit(move)
        self.stones[player] |= mark
        self.occupied |= mark
        return old

    def undo(self, move, player, raw):
        r, c = move
        self.board[r][c] = 0
        mark = bit(move)
        self.stones[player] ^= mark
        self.occupied ^= mark
        self.raw = raw

    def wins(self, player):
        return winning_cells(self.stones[player], self.occupied)


def _evaluate(pos, player):
    own, enemy = pos.raw[player - 1], pos.raw[2 - player]
    # Initiative belongs to the side to move, not an always-defensive coefficient.
    pressure = four_moves(pos.stones[player], pos.occupied).bit_count()
    danger = four_moves(pos.stones[3 - player], pos.occupied).bit_count()
    return int(own - enemy + 8000 * pressure - 9000 * danger)


def _ordered(pos, player, context, tt_move=None, forced=0):  # noqa: C901
    context.check()
    occupied, own, enemy = pos.occupied, pos.stones[player], pos.stones[3 - player]
    attacks = four_moves(own, occupied)
    enemy_forks = fork_moves(enemy, occupied)
    candidates = forced or (neighborhood(occupied, context.policy.radius) | attacks | enemy_forks)
    ranked = []
    for move in cells(candidates):
        context.check()
        old = pos.play(move, player)
        try:
            next_wins = pos.wins(player)
            safe = True
            if enemy_forks and not next_wins:
                safe = not fork_moves(enemy, pos.occupied)
            raw = pos.raw[player - 1] - pos.raw[2 - player]
            tactical = bool(next_wins or (enemy_forks and safe))
            priority = (next_wins.bit_count() >= 2, safe, bool(next_wins), raw,
                        -abs(move[0] - 7) - abs(move[1] - 7), -move[0], -move[1])
            ranked.append((priority, move, tactical))
        finally:
            pos.undo(move, player, old)
    ranked.sort(reverse=True)
    if enemy_forks and any(row[0][1] for row in ranked):
        ranked = [row for row in ranked if row[0][1]]
    # Tactical moves are retained beyond the quiet cap. TT promotion happens AFTER
    # membership selection; a stale ordering hint cannot change the searched tree.
    tactical = [row for row in ranked if row[2]]
    quiet = [row for row in ranked if not row[2]][:context.policy.quiet_limit]
    selected = tactical + quiet
    selected.sort(key=lambda row: (row[1] == tt_move, row[0]), reverse=True)
    stats = context.stats
    generated = candidates.bit_count()
    stats.generated_candidates += generated
    stats.candidate_cap_considered += generated
    stats.candidate_cap_pruned += generated - len(selected)
    stats.record_branching_factor(len(selected))
    return [row[1] for row in selected]


def _search(pos, player, depth, extensions, alpha, beta, ply, context):  # noqa: C901
    context.check(visit=True)
    stats = context.stats
    if pos.wins(player):
        stats.leaves += 1
        return MATE - ply - 1
    opponent_wins = pos.wins(3 - player)
    if opponent_wins.bit_count() >= 2:
        stats.leaves += 1
        return -MATE + ply + 2
    if pos.occupied == FULL:
        stats.leaves += 1
        return 0
    if depth <= 0 and not (extensions > 0 and (opponent_wins or four_moves(pos.stones[player], pos.occupied))):
        stats.leaves += 1
        return _evaluate(pos, player)
    # Never replace nominal depth with the extension depth in the cache key.
    # Exact remaining extension allowance is part of search semantics.
    key = (pos.stones[1], pos.stones[2], player, depth, extensions)
    alpha_start, beta_start = alpha, beta
    entry = None
    if context.use_tt:
        context.tt_probes += 1
        entry = context.table.get(key)
        if entry is not None:
            context.tt_hits += 1
            if entry.bound == EXACT:
                stats.leaves += 1
                return entry.score
            if entry.bound == LOWER:
                alpha = max(alpha, entry.score)
            else:
                beta = min(beta, entry.score)
            if alpha >= beta:
                return entry.score
    moves = _ordered(pos, player, context, entry.move if entry else None, opponent_wins)
    best, best_move = -INF, None
    for index, move in enumerate(moves):
        context.check()
        stats.expanded_candidates += 1
        old = pos.play(move, player)
        try:
            score = -_search(pos, 3 - player, depth - 1, extensions - int(depth <= 0),
                             -beta, -alpha, ply + 1, context)
        finally:
            pos.undo(move, player, old)
        if score > best:
            best, best_move = score, move
        alpha = max(alpha, best)
        if alpha >= beta:
            stats.alpha_beta_cutoffs += 1
            stats.alpha_beta_pruned += len(moves) - index - 1
            break
    if not moves:
        stats.leaves += 1
        best = 0
    context.save(key, best, alpha_start, beta_start, best_move)
    return best


def _prove_four(pos, attacker, remaining, ply, context):
    """Find a continuous-four win, returning None for unknown, never a false loss.

    Every accepted attack forces a unique reply or offers two distinct wins.
    Counter-wins for the defender refute that line. No unsearched branch is proof.
    """
    context.check(visit=True)
    context.proof_nodes += 1
    if context.proof_nodes > max(1, context.policy.node_limit // 4):
        raise Exhausted
    if remaining <= 0:
        context.stats.leaves += 1
        return None
    moves = four_moves(pos.stones[attacker], pos.occupied)
    context.stats.generated_candidates += moves.bit_count()
    context.stats.record_branching_factor(moves.bit_count())
    if not moves:
        context.stats.leaves += 1
    for move in cells(moves):
        context.check()
        context.stats.expanded_candidates += 1
        old = pos.play(move, attacker)
        try:
            threats = pos.wins(attacker)
            if pos.wins(3 - attacker):
                context.stats.leaves += 1
                continue
            if threats.bit_count() >= 2:
                context.stats.leaves += 1
                return move
            assert threats  # four_moves guarantees a next-turn winning cell.
            reply = next(cells(threats))
            context.stats.generated_candidates += 1
            context.stats.expanded_candidates += 1
            context.stats.record_branching_factor(1)
            defender_raw = pos.play(reply, 3 - attacker)
            try:
                if _prove_four(pos, attacker, remaining - 1, ply + 2, context) is not None:
                    return move
            finally:
                pos.undo(reply, 3 - attacker, defender_raw)
        finally:
            pos.undo(move, attacker, old)
    return None


def _root(pos, player, depth, context):
    moves = _ordered(pos, player, context)
    best, chosen = -INF, None
    for move in moves:
        context.check()
        context.stats.expanded_candidates += 1
        old = pos.play(move, player)
        try:
            # A later child only needs to prove it beats the current root best.
            # Refuted bounds never replace it; equal scores keep stable ordering.
            score = -_search(pos, 3 - player, depth - 1, context.policy.extensions, -INF, -best, 1, context)
        finally:
            pos.undo(move, player, old)
        if score > best:
            best, chosen = score, move
    return chosen, best


def _validate(board, player, policy, budget):
    if type(player) is not int or player not in (1, 2):
        raise ValueError('ai_player must be 1 or 2')
    if len(board) != 15 or any(len(row) != 15 for row in board):
        raise ValueError('board must be 15x15')
    if any(type(v) is not int or v not in (0, 1, 2) for row in board for v in row):
        raise ValueError('board cells must be integers 0, 1 or 2')
    if not math.isfinite(budget) or budget < 0:
        raise ValueError('time_budget_ms must be non-negative and finite')
    if policy.depth < 1 or policy.node_limit < 1:
        raise ValueError('depth and node_limit must be positive')


def choose_move(board, player, policy, *, time_budget_ms=None, use_tt=True):  # noqa: C901
    started = perf_counter()
    budget = policy.time_ms if time_budget_ms is None else time_budget_ms
    _validate(board, player, policy, budget)
    context = Context(policy, started + budget / 1000, use_tt=use_tt)
    pos = Position(board)
    legal = FULL ^ pos.occupied
    if not legal:
        raise ValueError('No legal candidate moves available for this board')
    move = min(cells(legal), key=lambda m: (abs(m[0] - 7) + abs(m[1] - 7), m))
    score, completed, fallback = 0, 0, True
    search_started = perf_counter()
    # The clock already runs. These fixed-size mandatory scans are retained even
    # at zero budget to guarantee an immediate win/unique block is never missed.
    own_wins, enemy_wins = pos.wins(player), pos.wins(3 - player)
    stats = context.stats
    stats.root_candidates = neighborhood(pos.occupied, policy.radius).bit_count()
    if own_wins:
        move, score, fallback = next(cells(own_wins)), MATE - 1, False
        stats.shortcut = 'immediate_win'
    elif enemy_wins.bit_count() == 1:
        move, score, fallback = next(cells(enemy_wins)), -1, False
        stats.shortcut = 'forced_block'
    elif enemy_wins.bit_count() >= 2:
        move, score, fallback = next(cells(enemy_wins)), -MATE + 2, False
        stats.shortcut = 'forced_loss'
    else:
        try:
            context.check()
            forks = fork_moves(pos.stones[player], pos.occupied)
            context.check()
            if forks:
                move, score, fallback = next(cells(forks)), MATE - 3, False
                stats.shortcut = 'proven_fork'
            else:
                # Proof search gets at most a quarter of the remaining clock so
                # an unknown proof cannot consume all ordinary-search time.
                if policy.proof_depth:
                    search_deadline = context.deadline
                    context.deadline = min(search_deadline, perf_counter() + budget / 4000)
                    try:
                        proof = _prove_four(pos, player, policy.proof_depth, 0, context)
                    except Exhausted:
                        proof = None
                    finally:
                        context.deadline = search_deadline
                    if proof is not None:
                        move, score, fallback = proof, MATE - 2 * policy.proof_depth - 1, False
                        stats.shortcut = 'proven_four_chain'
                if fallback:
                    for depth in range(1, policy.depth + 1):
                        chosen, value = _root(pos, player, depth, context)
                        if chosen is not None:
                            move, score, completed, fallback = chosen, value, depth, False
                        if abs(value) > MATE - 1000:
                            break
        except Exhausted:
            stats.timed_out = True
    finished = perf_counter()
    stats.elapsed_ms = (finished - started) * 1000
    result_stats = stats.to_dict()
    result_stats.update({'depth': completed, 'tt_probes': context.tt_probes, 'tt_hits': context.tt_hits,
                         'tt_hit_rate': context.tt_hits / context.tt_probes if context.tt_probes else 0.0,
                         'proof_nodes': context.proof_nodes, 'transposition_table_size': len(context.table),
                         'fallback_used': fallback, 'search_ms': (finished - search_started) * 1000,
                         'budget_ms': budget, 'stop_reason': (
                             'node_budget' if stats.nodes > policy.node_limit else 'deadline'
                         ) if stats.timed_out else (stats.shortcut if stats.shortcut != 'none' else 'depth')})
    return {'row': move[0], 'col': move[1], 'score': int(score),
            'elapsed_ms': round(stats.elapsed_ms, 3), 'search_stats': result_stats}
