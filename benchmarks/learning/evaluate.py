"""Complete paired-color, equal-budget experiments against the deployed core.

No experiment publishes a model or deploys code. A confidence interval supporting
an improvement, tactical gates and latency checks are required for promotion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from app.ai.competitive import choose_move, POLICIES
from benchmarks.competitive.metrics import paired_interval, percentile, provenance, wilson
from benchmarks.competitive.tournament import opening, play
from benchmarks.learning.model import Model
from benchmarks.learning.search import choose
from benchmarks.learning.train import board_key_from_prefix

PRODUCTION_SHA = 'c10ee2739b6577ea0004f86e91126dd176132319'


def verify_production(root):
    hashes = {}
    paths = sorted((root / 'app/ai').glob('*.py')) + sorted((root / 'app/domain').glob('*.py'))
    for path in paths:
        relative = str(path.relative_to(root))
        expected = subprocess.check_output(['git', 'show', PRODUCTION_SHA + ':' + relative], cwd=root)
        if path.read_bytes() != expected:
            raise ValueError('Production source changed: ' + relative)
        hashes[relative] = hashlib.sha256(expected).hexdigest()
    return hashes


def verify_holdout(model, manifest_path, seed, pairs):
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    if hashlib.sha256(raw).hexdigest() != model.metadata['training_manifest_sha256']:
        raise ValueError('Model and training manifest do not match')
    evaluation_keys = {board_key_from_prefix(opening(seed + i)) for i in range(pairs)}
    if not evaluation_keys <= set(manifest['reserved_root_keys']):
        raise ValueError('Evaluation openings were not reserved before training')
    if evaluation_keys.intersection(manifest['training_root_keys']):
        raise ValueError('Training/evaluation canonical opening leakage')
    return len(evaluation_keys)


def latency_summary(records, candidate):
    moves = [m for game in records for m in game['moves']
             if (m['player'] == game['candidate_color']) == candidate]
    times = [m['elapsed_ms'] for m in moves]
    return {'n': len(times), 'engine_p50_ms': percentile(times, .5), 'engine_p95_ms': percentile(times, .95),
            'engine_max_ms': max(times), 'timeouts': sum(m['stats'].get('timed_out', False) for m in moves),
            'fallbacks': sum(m['stats'].get('fallback_used', False) for m in moves),
            'nodes_mean': sum(m['stats'].get('nodes', 0) for m in moves) / len(moves),
            'note': 'Tournament positions differ by side; not a same-fixture speedup measurement.'}


def experiment(args):  # noqa: C901
    if args.games < 200 or args.games % 2:
        raise ValueError('Initial strength comparison requires an even number of at least 200 complete games')
    root = Path(__file__).resolve().parents[2]
    hashes = verify_production(root)
    model = Model.load(args.model)
    unique = verify_holdout(model, args.training_manifest, args.seed, args.games // 2)
    initial = Model.load(args.initial_model) if args.opponent == 'initial' else None
    if initial and initial.digest() != model.metadata['initial_model_sha256']:
        raise ValueError('Ablation opponent is not the recorded initial model')

    def contender(board, player, level, budget, seed=0):
        return choose(board, player, level, budget, model)

    def opponent(board, player, level, budget, seed=0):
        if initial:
            return choose(board, player, level, budget, initial)
        return choose_move(board, player, POLICIES[level], time_budget_ms=budget)

    # Excluded warm-up on a separate opening; each contender gets the same board.
    warm = [[0] * 15 for _ in range(15)]
    warm[7][7], warm[7][8] = 1, 2
    for adapter in (contender, opponent):
        adapter(warm, 1, args.level, args.budget_ms)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    records, clusters = [], {}
    with args.output.with_suffix('.jsonl').open('w') as raw:
        for pair in range(args.games // 2):
            for color in (1, 2):
                game = play(contender if color == 1 else opponent, opponent if color == 1 else contender,
                            args.seed + pair, args.budget_ms, (args.level, args.level))
                game['candidate_color'] = color
                game['candidate_score'] = .5 if not game['winner'] else float(game['winner'] == color)
                records.append(game)
                clusters.setdefault(board_key_from_prefix(game['opening']), []).append(game['candidate_score'])
                raw.write(json.dumps(game, separators=(',', ':')) + '\n')
                raw.flush()
            if (pair + 1) % 10 == 0:
                print(f'{args.opponent}: {len(records)}/{args.games} complete games', flush=True)
    wins = sum(r['candidate_score'] == 1 for r in records)
    draws = sum(r['candidate_score'] == .5 for r in records)
    interval = paired_interval([sum(values) / len(values) for values in clusters.values()])
    report = {'games': len(records), 'wins': wins, 'draws': draws, 'losses': len(records) - wins - draws,
              'score_rate': (wins + .5 * draws) / len(records), 'win_rate_wilson95': wilson(wins, len(records)),
              'canonical_opening_score_bootstrap95': interval, 'canonical_openings': unique,
              'bootstrap_estimand': 'Equal-weight D4-canonical board opening clusters, not independent game wins.',
              'strength_gate': 'SUPPORTED_ON_THIS_OPENING_DISTRIBUTION' if interval[0] > .5 else 'NOT_ESTABLISHED',
              'production_source_sha': PRODUCTION_SHA, 'production_file_hashes': hashes,
              'candidate_model_sha256': model.digest(), 'opponent_model_sha256': initial.digest() if initial else None,
              'protocol': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
              'environment': provenance(root), 'candidate_latency': latency_summary(records, True),
              'opponent_latency': latency_summary(records, False),
              'promotion': 'NOT_AUTOMATIC: strength alone does not satisfy challenge/tactical/latency gates.'}
    for who in ('candidate', 'opponent'):
        for kind in ('win', 'block'):
            def side(game):
                return game['candidate_color'] - 1 if who == 'candidate' else 2 - game['candidate_color']
            report[f'{who}_missed_{kind}'] = {
                'misses': sum(r['misses'][kind][side(r)] for r in records),
                'opportunities': sum(r['opportunities'][kind][side(r)] for r in records)}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('environment', 'production_file_hashes')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--initial-model', type=Path)
    parser.add_argument('--training-manifest', type=Path, required=True)
    parser.add_argument('--opponent', choices=['production', 'initial'], default='production')
    parser.add_argument('--level', choices=['HARD', 'IMPOSSIBLE'], default='IMPOSSIBLE')
    parser.add_argument('--budget-ms', type=float, default=700)
    parser.add_argument('--games', type=int, default=200)
    parser.add_argument('--seed', type=int, default=20300101)
    parser.add_argument('--output', type=Path, required=True)
    experiment(parser.parse_args())
