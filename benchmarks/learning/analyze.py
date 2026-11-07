"""Locate the earliest certifiable tactical error, not an invented first blunder."""
import argparse
import hashlib
import json
from pathlib import Path

from app.ai.threats import FULL, bit, cells, encode
from benchmarks.competitive.corpus import wins
from benchmarks.learning.certificates import Solver, verify_certificate
from benchmarks.learning.records import load_games, private_output, validate_game
from benchmarks.learning.witness import prove_plan, verify_plan


def first_plan_error(positions, depth, max_nodes):
    """Try observed forcing continuations; quantify only the demonstrated plan."""
    for index, (board, player, actual) in enumerate(positions):
        if player != 2 or wins(board, player) or wins(board, 3 - player):
            continue
        changed = [row[:] for row in board]
        changed[actual[0]][actual[1]] = player
        future = [positions[i][2] for i in range(index + 1, min(len(positions), index + 9), 2)]
        for length in range(1, len(future) + 1):
            plan = future[:length]
            status, certificate = prove_plan(changed, 3 - player, plan, depth, max_nodes)
            if status != 'PROVEN':
                continue
            verify_plan(changed, 3 - player, certificate)
            alternatives, unknown = [], 0
            for r in range(15):
                for c in range(15):
                    if board[r][c]:
                        continue
                    alternative = [row[:] for row in board]
                    alternative[r][c] = player
                    result, _ = prove_plan(alternative, 3 - player, plan, depth, max_nodes)
                    if result == 'NO_PROOF':
                        alternatives.append((r, c))
                    unknown += result == 'UNKNOWN'
            if alternatives:
                return {'ply': index + 1, 'board': board, 'player': player, 'actual_move': actual,
                        'kind': 'allows_certified_observed_attack_plan', 'observed_human_plan': plan,
                        'expected_moves': alternatives, 'unknown_alternatives': unknown,
                        'certificate': certificate, 'forcing_attack_depth': depth,
                        'expected_scope': 'Refutes this observed attack plan; no full-game winning/safe-move claim.'}
    return None


def inspect_position(board, player, actual, depth, max_nodes):
    own = wins(board, player)
    enemy = wins(board, 3 - player)
    if own:
        return {'kind': 'missed_immediate_win', 'expected_moves': sorted(own)} if actual not in own else None
    if len(enemy) == 1 and actual not in enemy:
        return {'kind': 'missed_unique_block', 'expected_moves': sorted(enemy)}
    stones = encode(board)
    own, enemy = stones[player], stones[3 - player]
    solver = Solver(max_nodes)
    after = solver.solve(enemy, own | bit(actual), depth)
    if after.status != 'PROVEN':
        return None
    changed = [row[:] for row in board]
    changed[actual[0]][actual[1]] = player
    verify_certificate(changed, 3 - player, after.line)
    alternatives, unknown = [], 0
    for move in cells(FULL ^ (own | enemy)):
        result = solver.solve(enemy, own | bit(move), depth)
        unknown += result.status == 'UNKNOWN'
        if result.status == 'NO_PROOF':
            alternatives.append(move)
    return {
        'kind': 'allows_bounded_forcing_win' if alternatives else 'already_forced_or_unresolved',
        'forcing_attack_depth': depth, 'certificate': after.line,
        'expected_moves': sorted(alternatives), 'unknown_alternatives': unknown,
        'expected_scope': 'Excludes opponent continuous-four proofs within this attack horizon; not guaranteed game wins.',
    }


def analyze(path, depth, max_nodes):
    dataset = load_games(path)
    output = []
    for game in dataset['games']:
        positions = validate_game(game)
        detected = []
        for ply, (board, player, actual) in enumerate(positions, 1):
            if player != 2:
                continue
            finding = inspect_position(board, player, actual, depth, max_nodes)
            if finding:
                detected.append({'ply': ply, 'board': board, 'player': player,
                                 'actual_move': actual, **finding})
            if finding and finding['expected_moves']:
                break
        output.append({'game_id': game['game_id'], 'move_count': game['move_count'],
                       'recorded_difficulty': game.get('difficulty'), 'findings': detected,
                       'first_observed_plan_error': first_plan_error(positions, depth, max_nodes),
                       'label': 'Earliest detected certifiable error, not a proven first strategic mistake'})
    return {'dataset_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'comparison_source_sha': 'c10ee2739b6577ea0004f86e91126dd176132319',
            'scope': 'Retrospective bounded-model diagnosis; exact game-time engine/difficulty unavailable.',
            'games': output}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--depth', type=int, default=3)
    parser.add_argument('--max-nodes', type=int, default=30000)
    args = parser.parse_args()
    report = analyze(args.dataset, args.depth, args.max_nodes)
    private_output(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'complete_games': len(report['games']),
                      'certified_observed_plan_findings': sum(bool(g['first_observed_plan_error']) for g in report['games']),
                      'private_details': 'Saved locally; no game identifiers, moves or boards printed.'}))
