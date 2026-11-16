"""Experimental learned root ordering/value prior; production routing is untouched.

The heads choose/rank root candidates. An apparent loss in the selective tree
widens root coverage instead of stopping early. Deeper search and terminal proofs
use the frozen production core. No globals or production functions mutate.
"""
from dataclasses import replace
import os
from pathlib import Path
from time import perf_counter

from app.ai.competitive import (
    Context, Exhausted, INF, MATE, POLICIES, Position, _ordered, _prove_four, _search, _validate,
)
from app.ai.threats import FULL, bit, cells, fork_moves, neighborhood
from benchmarks.learning.model import Model, action_features


def ranked_roots(pos, player, context, model):
    original = context.policy
    try:
        context.policy = replace(original, quiet_limit=225)
        moves = _ordered(pos, player, context)
    finally:
        context.policy = original
    enemy_forks = fork_moves(pos.stones[3 - player], pos.occupied)
    ranked = []
    for move in moves:
        context.check()
        features, after_value = action_features(pos, player, move)
        priority = float(model.logits(features) + .3 * model.predict(after_value))
        forced = bool(features[3] or (enemy_forks and not fork_moves(
            pos.stones[3 - player], pos.occupied | bit(move))))
        ranked.append((priority, move, forced))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    chosen = select_roots(ranked, original.quiet_limit)
    context.stats.candidate_cap_pruned += len(moves) - len(chosen)
    context.stats.branching_factor_sum -= len(moves) - len(chosen)
    return chosen, ranked


def select_roots(ranked, quiet_limit):
    quiet = [row for row in ranked if not row[2]][:quiet_limit]
    chosen = [row for row in ranked if row[2]] + quiet
    chosen.sort(key=lambda row: (-row[0], row[1]))
    return [row[1] for row in chosen]


def root_iteration(pos, player, moves, depth, context):
    best, chosen = -INF, None
    for move in moves:
        context.check()
        context.stats.expanded_candidates += 1
        old = pos.play(move, player)
        try:
            score = -_search(pos, 3 - player, depth - 1, context.policy.extensions, -INF, -best, 1, context)
        finally:
            pos.undo(move, player, old)
        if score > best:
            best, chosen = score, move
    return chosen, best


def choose(board, player, level, budget_ms, model):  # noqa: C901
    started = perf_counter()
    policy = POLICIES[level]
    budget = policy.time_ms if budget_ms is None else budget_ms
    _validate(board, player, policy, budget)
    context = Context(policy, started + budget / 1000)
    pos = Position(board)
    legal = FULL ^ pos.occupied
    if not legal:
        raise ValueError('No legal moves')
    move = min(cells(legal), key=lambda m: (abs(m[0] - 7) + abs(m[1] - 7), m))
    score, completed, fallback = 0, 0, True
    own, enemy = pos.wins(player), pos.wins(3 - player)
    stats = context.stats
    stats.root_candidates = neighborhood(pos.occupied, policy.radius).bit_count()
    if own:
        move, score, fallback = next(cells(own)), MATE - 1, False
        stats.shortcut = 'immediate_win'
    elif enemy:
        move, fallback = next(cells(enemy)), False
        score = -MATE + 2 if enemy.bit_count() >= 2 else -1
        stats.shortcut = 'forced_loss' if enemy.bit_count() >= 2 else 'forced_block'
    else:
        try:
            context.check()
            forks = fork_moves(pos.stones[player], pos.occupied)
            context.check()
            if forks:
                move, score, fallback = next(cells(forks)), MATE - 3, False
                stats.shortcut = 'proven_fork'
            if fallback and policy.proof_depth:
                deadline = context.deadline
                context.deadline = min(deadline, perf_counter() + budget / 4000)
                try:
                    proof = _prove_four(pos, player, policy.proof_depth, 0, context)
                except Exhausted:
                    proof = None
                finally:
                    context.deadline = deadline
                if proof is not None:
                    move, score, fallback = proof, MATE - 2 * policy.proof_depth - 1, False
                    stats.shortcut = 'proven_four_chain'
            if fallback:
                moves, ranked = ranked_roots(pos, player, context, model)
                if moves:
                    move = moves[0]
                depth, cap = 1, policy.quiet_limit
                while depth <= policy.depth:
                    chosen, result = root_iteration(pos, player, moves, depth, context)
                    if chosen is not None:
                        move, score, completed, fallback = chosen, result, depth, False
                    if result < -MATE + 1000 and len(moves) < len(ranked):
                        cap *= 2
                        widened = select_roots(ranked, cap)
                        increase = len(widened) - len(moves)
                        stats.candidate_cap_pruned -= increase
                        stats.branching_factor_sum += increase
                        moves = widened
                        continue
                    depth += 1
        except Exhausted:
            stats.timed_out = True
    stats.elapsed_ms = (perf_counter() - started) * 1000
    values = stats.to_dict()
    values.update({'depth': completed, 'fallback_used': fallback, 'budget_ms': budget,
                   'tt_probes': context.tt_probes, 'tt_hits': context.tt_hits,
                   'stop_reason': 'budget' if stats.timed_out else stats.shortcut,
                   'model_sha256': model.digest()})
    return {'row': move[0], 'col': move[1], 'score': int(score),
            'elapsed_ms': stats.elapsed_ms, 'search_stats': values}


_MODELS = {}


def challenger(board, player, difficulty, budget_ms, seed=0):
    path = Path(os.environ['CAROAI_OFFLINE_MODEL']).resolve()
    # File fingerprint prevents stale models when a path is intentionally reused.
    signature = path, path.stat().st_mtime_ns, path.stat().st_size
    if signature not in _MODELS:
        _MODELS[signature] = Model.load(path)
    return choose(board, player, difficulty, budget_ms, _MODELS[signature])
