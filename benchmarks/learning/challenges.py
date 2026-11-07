"""Measure production and candidate on human plans and the independent corpus."""
import argparse
import json
from pathlib import Path

from app.ai.competitive import POLICIES, choose_move
from benchmarks.competitive.corpus import cases, transform_cell
from benchmarks.learning.model import Model
from benchmarks.learning.records import private_output
from benchmarks.learning.search import choose


def variants(case):
    for rotation in range(4):
        for reflect in range(2):
            for swap in (False, True):
                board = [[0] * 15 for _ in range(15)]
                for r in range(15):
                    for c in range(15):
                        rr, cc = transform_cell((r, c), rotation, reflect)
                        value = case['board'][r][c]
                        board[rr][cc] = 3 - value if swap and value else value
                expected = {transform_cell(move, rotation, reflect) for move in case['expected_moves']}
                yield board, 3 - case['player'] if swap else case['player'], expected


def measure(model, private_challenges=None):
    challenges = json.loads(private_challenges.read_text())['cases'] if private_challenges else []
    report = {'scope': 'Observed-plan refutations, not guaranteed game wins; no human positions used for gradient training.',
              'model_sha256': model.digest(), 'human_cases': [], 'tactical': []}
    for case in challenges:
        row = {'name': case['name'], 'ply': case['ply'], 'n': 0, 'production_pass': 0, 'candidate_pass': 0}
        for board, player, expected in variants(case):
            row['n'] += 1
            for name, result in (
                ('production', choose_move(board, player, POLICIES['IMPOSSIBLE'])),
                ('candidate', choose(board, player, 'IMPOSSIBLE', 700, model)),
            ):
                row[name + '_pass'] += (result['row'], result['col']) in expected
        report['human_cases'].append(row)
    for level in ('HARD', 'IMPOSSIBLE'):
        row = {'level': level, 'n': 0, 'candidate_pass': 0}
        for case in cases():
            board = case.board()
            before = [r[:] for r in board]
            result = choose(board, case.player, level, None, model)
            row['n'] += 1
            row['candidate_pass'] += (result['row'], result['col']) in case.expected_moves
            if board != before:
                raise AssertionError('Candidate mutated corpus input')
        report['tactical'].append(row)
    report['all_challenges_pass'] = (all(x['candidate_pass'] == x['n'] for x in report['human_cases'])
                                     if challenges else None)
    report['human_validation_scope'] = 'PRIVATE_LOCAL_DATA' if challenges else 'NOT_RUN_PUBLIC_CI'
    report['all_tactics_pass'] = all(x['candidate_pass'] == x['n'] for x in report['tactical'])
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--private-challenges', type=Path,
                        help='Optional local owner-controlled data; never auto-upload to public artifacts')
    args = parser.parse_args()
    report = measure(Model.load(args.model), args.private_challenges)
    output = private_output(args.output) if args.private_challenges else args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    if args.private_challenges:
        print(json.dumps({'model_sha256': report['model_sha256'],
                          'private_cases': sum(g['n'] for g in report['human_cases']),
                          'candidate_pass': sum(g['candidate_pass'] for g in report['human_cases']),
                          'all_challenges_pass': report['all_challenges_pass']}))
    else:
        print(json.dumps(report, indent=2))
