"""Summarize prespecified research gates; never publish or change production."""
import argparse
import json
from pathlib import Path


def decide(root):
    def read(name):
        return json.loads((root / name).read_text())
    challenges = read('challenges.json')
    production = read('production-impossible-700.json')
    initial = read('initial-impossible-700.json')
    hard = read('production-hard-250.json')
    latency = read('engine.json')
    serial = next(g for g in latency['groups'] if g['adapter'] == 'candidate' and g['concurrency'] == 1)
    comparisons = [production, initial, hard, read('production-impossible-25.json')]
    model_hashes = {r['candidate_model_sha256'] for r in comparisons}
    if (len(model_hashes) != 1 or challenges['model_sha256'] not in model_hashes
            or latency['model_sha256'] not in model_hashes):
        raise ValueError('Cannot combine results from different models')
    checks = {
        'tactical_480': challenges['all_tactics_pass'],
        'human_plan_48': challenges['all_challenges_pass'],
        'beats_production_700': production['canonical_opening_score_bootstrap95'][0] > .5,
        'learning_beats_untrained_algorithm': initial['canonical_opening_score_bootstrap95'][0] > .5,
        'hard_noninferior_5points': hard['canonical_opening_score_bootstrap95'][0] >= .45,
        'serial_p95_within_770ms': serial['p95_ms'] <= 770,
        'zero_serial_fallbacks': serial['fallbacks'] == 0,
        'no_missed_immediate_tactics': all(
            r['candidate_missed_' + kind]['misses'] == 0
            for r in comparisons for kind in ('win', 'block')),
    }
    return {'model_sha256': next(iter(model_hashes)), 'checks': checks,
            'decision': 'ELIGIBLE_FOR_REVIEW' if all(checks.values()) else 'NOT_PROMOTED',
            'failed_gates': [k for k, passed in checks.items() if not passed],
            'production_changes': False,
            'scope': 'No deployment. Human-play balance and candidate API/capacity remain unmeasured.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = decide(args.results)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
