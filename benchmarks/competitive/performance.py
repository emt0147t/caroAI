"""Same-process controlled engine comparison; engine contention is not API latency."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from time import perf_counter

from benchmarks.competitive.adapters import baseline, candidate, verify_baseline
from benchmarks.competitive.metrics import percentile, provenance
from scripts.benchmark_ai_sprint3 import build_fixtures


def trial(adapter, fixture, level, budget):
    board = [row[:] for row in fixture['board']]
    before = [row[:] for row in board]
    start = perf_counter()
    result = adapter(board, fixture['ai_player'], level, budget)
    elapsed = (perf_counter() - start) * 1000
    r, c = result['row'], result['col']
    if board != before or not (0 <= r < 15 and 0 <= c < 15) or board[r][c]:
        raise AssertionError('illegal move or mutated input')
    stats = result.get('search_stats', {})
    return {'engine_ms': elapsed, 'search_ms': stats.get('search_ms'), 'move': [r, c], **stats}


def run(args):
    baseline_hashes = verify_baseline()
    raw, groups = [], []
    fixtures = build_fixtures()
    empty = [[0] * 15 for _ in range(15)]
    fixtures += [{'name': 'empty_opening', 'category': 'opening', 'board': empty, 'ai_player': 1}]
    for level in ('EASY', 'MEDIUM', 'HARD', 'IMPOSSIBLE'):
        for concurrency in args.concurrency:
            rows = {'baseline': [], 'candidate': []}
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                for fixture in fixtures:
                    for repetition in range(-args.warmup, args.runs):
                        # Alternate order to avoid a systematic cold/warm advantage.
                        adapters = [('baseline', baseline), ('candidate', candidate)]
                        if repetition % 2:
                            adapters.reverse()
                        for name, adapter in adapters:
                            calls = [pool.submit(trial, adapter, fixture, level, args.budget_ms)
                                     for _ in range(concurrency)]
                            for future in calls:
                                row = {'adapter': name, 'difficulty': level, 'concurrency': concurrency,
                                       'fixture': fixture['name'], 'trial': repetition, 'warmup': repetition < 0, **future.result()}
                                raw.append(row)
                                if repetition >= 0:
                                    rows[name].append(row)
            for name, records in rows.items():
                times = [r['engine_ms'] for r in records]
                search = [r for r in records if r.get('shortcut', 'none') == 'none']
                times_search = [r['search_ms'] for r in search if r.get('search_ms') is not None]
                expanded = sum(r.get('expanded_candidates', 0) for r in records)
                pruned = sum(r.get('alpha_beta_pruned', 0) for r in records)
                probes = sum(r.get('tt_probes', 0) for r in records)
                branching_nodes = sum(r.get('branching_factor_nodes', 0) for r in records)
                groups.append({'adapter': name, 'difficulty': level, 'concurrency': concurrency, 'n': len(records),
                               'p50_ms': percentile(times, .5), 'p95_ms': percentile(times, .95), 'max_ms': max(times),
                               'timeouts': sum(bool(r.get('timed_out')) for r in records),
                               'fallbacks': sum(bool(r.get('fallback_used')) for r in records),
                               'search_only_n': len(search), 'search_only_p50_ms': percentile(times_search, .5),
                               'search_only_p95_ms': percentile(times_search, .95),
                               'nodes_mean': sum(r.get('nodes', 0) for r in records) / len(records),
                               'effective_branching': sum(r.get('branching_factor_sum', 0) for r in records)
                               / branching_nodes if branching_nodes else 0,
                               'alpha_beta_pruning_rate': pruned / (expanded + pruned) if expanded + pruned else 0,
                               'tt_hit_rate': sum(r.get('tt_hits', 0) for r in records) / probes if probes else 0})
            print(level, concurrency, 'complete', flush=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix('.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in raw))
    output.write_text(json.dumps({'environment': provenance(Path(__file__).resolve().parents[2]),
                                 'protocol': vars(args), 'groups': groups, 'baseline_files_sha256': baseline_hashes,
                                 'scope': 'In-process engine threads, not network API or production latency.'}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=int, default=5)
    parser.add_argument('--warmup', type=int, default=1)
    parser.add_argument('--concurrency', nargs='+', type=int, default=[1, 2, 4, 8])
    parser.add_argument('--budget-ms', type=float, default=None)
    parser.add_argument('--output', required=True)
    run(parser.parse_args())
