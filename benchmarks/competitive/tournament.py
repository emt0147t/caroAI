"""Color-paired full-game tournament; no adjudicated draws or self-play-only claim.

Use --adapter module:function for candidate/baseline adapters returning engine dicts.
Each seed is a paired opening cluster, with the contender changing colors. Raw logs
retain every move, missed tactical opportunities, timeouts and the terminal reason.
"""
import argparse
import importlib
import json
import random
from pathlib import Path
from time import perf_counter_ns

from app.domain.game_rules import GameRules
from app.domain.game_state import GameState, GameStatus, Player
from benchmarks.competitive.corpus import wins
from benchmarks.competitive.metrics import paired_interval, provenance, wilson


def load_adapter(spec):
    module, function = spec.split(':')
    return getattr(importlib.import_module(module), function)


def opening(seed):
    rng = random.Random(seed)
    styles = [((7, 7), (7, 8)), ((7, 7), (6, 6)), ((3, 3), (3, 4)),
              ((7, 7), (5, 7)), ((11, 4), (10, 5))]
    result = list(styles[seed % len(styles)])
    # Different seeds perturb the orientation and a legal third move.
    rotation, reflect = rng.randrange(4), rng.randrange(2)
    from benchmarks.competitive.corpus import transform_cell
    return [transform_cell(m, rotation, reflect) for m in result]


def play(first, second, seed, budget_ms, levels):
    state = GameState()
    prefix = opening(seed)
    history = []
    opportunities = {'win': [0, 0], 'block': [0, 0]}
    misses = {'win': [0, 0], 'block': [0, 0]}
    for move in prefix:
        GameRules.apply_move(state, *move)
    while state.status == GameStatus.IN_PROGRESS:
        player = 1 if state.current_player == Player.X else 2
        board = [[{'EMPTY': 0, 'X': 1, 'O': 2}[v] for v in row] for row in state.board]
        before = [row[:] for row in board]
        own_wins, enemy_wins = wins(board, player), wins(board, 3 - player)
        start = perf_counter_ns()
        output = (first if player == 1 else second)(board, player, levels[player - 1], budget_ms, seed)
        elapsed = (perf_counter_ns() - start) / 1e6
        if board != before:
            raise AssertionError('engine mutated board')
        move = output['row'], output['col']
        if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < 15 for v in move):
            raise AssertionError('invalid coordinates')
        if own_wins:
            opportunities['win'][player - 1] += 1
            misses['win'][player - 1] += int(move not in own_wins)
        elif len(enemy_wins) == 1:
            opportunities['block'][player - 1] += 1
            misses['block'][player - 1] += int(move not in enemy_wins)
        GameRules.apply_move(state, *move)
        history.append({'player': player, 'move': move, 'elapsed_ms': elapsed,
                        'stats': output.get('search_stats', {})})
    winner = 1 if state.winner == Player.X else 2 if state.winner == Player.O else 0
    return {'seed': seed, 'opening': prefix, 'winner': winner, 'terminal': state.status.value,
            'moves': history, 'opportunities': opportunities, 'misses': misses}


def run(args):
    if args.games < 200 or args.games % 2:
        raise ValueError('initial comparison requires an even number of at least 200 games')
    candidate, opponent = load_adapter(args.candidate), load_adapter(args.opponent)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    results, pair_scores = [], []
    with path.with_suffix('.jsonl').open('w') as raw:
        for pair in range(args.games // 2):
            scores = []
            for color in (1, 2):
                result = play(candidate if color == 1 else opponent, opponent if color == 1 else candidate,
                              args.seed + pair, args.budget_ms,
                              (args.candidate_level, args.opponent_level) if color == 1
                              else (args.opponent_level, args.candidate_level))
                result['candidate_color'] = color
                result['candidate_score'] = .5 if result['winner'] == 0 else float(result['winner'] == color)
                scores.append(result['candidate_score'])
                results.append(result)
                raw.write(json.dumps(result, separators=(',', ':')) + '\n')
                raw.flush()
            pair_scores.append(sum(scores) / 2)
            if (pair + 1) % 10 == 0:
                print(f'{args.candidate_level} vs {args.opponent_level}: {2 * (pair + 1)}/{args.games}', flush=True)
    won = sum(r['candidate_score'] == 1 for r in results)
    drawn = sum(r['candidate_score'] == .5 for r in results)
    summary = {'protocol': vars(args), 'environment': provenance(Path(__file__).resolve().parents[2]),
               'games': len(results), 'wins': won, 'draws': drawn, 'losses': len(results) - won - drawn,
               'score_rate': (won + .5 * drawn) / len(results), 'win_rate_wilson95': wilson(won, len(results)),
               'score_rate_paired_bootstrap95': paired_interval(pair_scores),
               'note': 'Screening at specified per-move budget; not default-budget or production strength evidence.'}
    for kind in ('win', 'block'):
        for who in ('candidate', 'opponent'):
            idx = lambda r: r['candidate_color'] - 1 if who == 'candidate' else 2 - r['candidate_color']
            n = sum(r['opportunities'][kind][idx(r)] for r in results)
            missed = sum(r['misses'][kind][idx(r)] for r in results)
            summary[f'{who}_missed_{kind}'] = {'misses': missed, 'opportunities': n,
                                               'rate': missed / n if n else None}
    path.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('environment', 'protocol')}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', default='benchmarks.competitive.adapters:candidate')
    p.add_argument('--opponent', default='benchmarks.competitive.adapters:baseline')
    p.add_argument('--candidate-level', default='HARD')
    p.add_argument('--opponent-level', default='HARD')
    p.add_argument('--games', type=int, default=200)
    p.add_argument('--seed', type=int, default=20261107)
    p.add_argument('--budget-ms', type=float, default=25)
    p.add_argument('--output', required=True)
    run(p.parse_args())


if __name__ == '__main__':
    main()
