"""Convert owner-controlled analysis into a local, independently checked corpus."""
import argparse
import hashlib
import json
from pathlib import Path

from app.ai.competitive import _validate, POLICIES
from benchmarks.learning.records import private_output
from benchmarks.learning.witness import prove_plan, verify_plan


def build(report):
    cases = []
    for game in report['games']:
        finding = game.get('first_observed_plan_error')
        if not finding:
            continue
        board, player = finding['board'], finding['player']
        _validate(board, player, POLICIES['IMPOSSIBLE'], 0)
        move = finding['actual_move']
        after = [row[:] for row in board]
        if after[move[0]][move[1]]:
            raise ValueError('Recorded AI move is occupied')
        after[move[0]][move[1]] = player
        verify_plan(after, 3 - player, finding['certificate'])
        accepted = finding['expected_moves']
        if not accepted or move in accepted or finding['unknown_alternatives']:
            raise ValueError('Incomplete/uncertain expected set cannot be promoted to a challenge')
        for alternative in accepted:
            changed = [row[:] for row in board]
            r, c = alternative
            if changed[r][c]:
                raise ValueError('Expected move is occupied')
            changed[r][c] = player
            status, _ = prove_plan(changed, 3 - player, finding['observed_human_plan'],
                                   finding['forcing_attack_depth'])
            if status != 'NO_PROOF':
                raise ValueError('Expected move did not refute the demonstrated plan')
        fields = ('ply', 'board', 'player', 'actual_move', 'observed_human_plan',
                  'expected_moves', 'forcing_attack_depth', 'expected_scope')
        cases.append({'name': f'private-case-{len(cases) + 1}',
                      'source_game_fingerprint': hashlib.sha256(game['game_id'].encode()).hexdigest(),
                      **{key: finding[key] for key in fields}})
    if not cases:
        raise ValueError('No certified cases found; an empty private corpus is not a PASS')
    return {'schema_version': 1, 'scope': 'Private development regressions, never a full-game safety proof.',
            'cases': cases}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    corpus = build(json.loads(args.analysis.read_text()))
    private_output(args.output).write_text(json.dumps(corpus, indent=2) + '\n')
    print(f"Created {len(corpus['cases'])} local private cases; no upload or database write.")
