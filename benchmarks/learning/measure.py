"""Paired same-fixture core latency; threaded stress is not API latency."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from time import perf_counter

from app.ai.competitive import POLICIES, choose_move
from benchmarks.competitive.metrics import percentile, provenance
from benchmarks.learning.evaluate import verify_production
from benchmarks.learning.model import Model
from benchmarks.learning.search import choose
from scripts.benchmark_ai_sprint3 import build_fixtures


def trial(adapter, fixture, budget, level):
    board = [r[:] for r in fixture['board']]
    original = [r[:] for r in board]
    start = perf_counter()
    result = adapter(board, fixture['ai_player'], level, budget)
    elapsed = (perf_counter() - start) * 1000
    r, c = result['row'], result['col']
    assert board == original and original[r][c] == 0
    return {'engine_ms': elapsed, 'move': [r, c], 'stats': result['search_stats']}


def measure(args):
    verify_production(Path(__file__).resolve().parents[2])
    model = Model.load(args.model)
    adapters = {
        'production': lambda b, p, level, budget: choose_move(b, p, POLICIES[level], time_budget_ms=budget),
        'candidate': lambda b, p, level, budget: choose(b, p, level, budget, model),
    }
    fixtures = build_fixtures() + [{'name': 'empty_opening', 'board': [[0] * 15 for _ in range(15)], 'ai_player': 1}]
    rows, groups = [], []
    for concurrency in args.concurrency:
        with ThreadPoolExecutor(concurrency) as pool:
            for fixture in fixtures:
                for repetition in range(-args.warmup, args.runs):
                    order = list(adapters)
                    if repetition % 2:
                        order.reverse()
                    for name in order:
                        futures = [pool.submit(trial, adapters[name], fixture, args.budget_ms, args.level)
                                   for _ in range(concurrency)]
                        for future in futures:
                            rows.append({'adapter': name, 'fixture': fixture['name'], 'concurrency': concurrency,
                                         'trial': repetition, 'warmup': repetition < 0, **future.result()})
        for name in adapters:
            calls = [r for r in rows if r['concurrency'] == concurrency and r['adapter'] == name and not r['warmup']]
            times = [r['engine_ms'] for r in calls]
            groups.append({'adapter': name, 'concurrency': concurrency, 'n': len(calls),
                           'p50_ms': percentile(times, .5), 'p95_ms': percentile(times, .95), 'max_ms': max(times),
                           'timeouts': sum(r['stats'].get('timed_out', False) for r in calls),
                           'fallbacks': sum(r['stats'].get('fallback_used', False) for r in calls),
                           'nodes_mean': sum(r['stats'].get('nodes', 0) for r in calls) / len(calls)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    report = {'environment': provenance(Path(__file__).resolve().parents[2]), 'groups': groups,
              'protocol': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
              'model_sha256': model.digest(), 'scope': 'Same-process/fixture paired core comparison; not HTTP/production SLO.'}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(groups, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--level', choices=['HARD', 'IMPOSSIBLE'], default='IMPOSSIBLE')
    parser.add_argument('--budget-ms', type=float, default=700)
    parser.add_argument('--runs', type=int, default=5)
    parser.add_argument('--warmup', type=int, default=1)
    parser.add_argument('--concurrency', type=int, nargs='+', default=[1, 2, 4, 8])
    parser.add_argument('--output', type=Path, required=True)
    measure(parser.parse_args())
