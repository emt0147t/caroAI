"""Independent domain replay of complete self-play and evaluation artifacts."""
import argparse
import hashlib
import json
from pathlib import Path

from app.domain.game_rules import GameRules
from app.domain.game_state import GameState, Player
from benchmarks.learning.records import board_key, numeric_board


def audit(path, manifest_path=None):
    count, plies = 0, 0
    manifest = json.loads(manifest_path.read_text()) if manifest_path else None
    reserved = set(manifest['reserved_root_keys']) if manifest else set()
    roots = set()
    if manifest:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest['selfplay_sha256']
    for line in path.read_text().splitlines():
        game = json.loads(line)
        state = GameState()
        for move in game['opening']:
            GameRules.apply_move(state, *move)
        root = board_key(numeric_board(state), 1)
        roots.add(root)
        if manifest:
            assert root == game['root_canonical_key'] and root not in reserved
        for move in game['moves']:
            if manifest and state.move_count <= 8:
                assert board_key(numeric_board(state), 1) not in reserved
            player = 1 if state.current_player == Player.X else 2
            assert move['player'] == player
            if 'move' in move:
                r, c = move['move']
            else:
                assert move['ply'] == state.move_count + 1
                r, c = move['row'], move['col']
            GameRules.apply_move(state, r, c)
            plies += 1
        winner = 1 if state.winner == Player.X else 2 if state.winner == Player.O else 0
        assert state.status.value in ('X_WON', 'O_WON', 'DRAW')
        assert state.status.value == game['terminal'] and winner == game['winner']
        if 'candidate_score' in game:
            assert game['candidate_score'] == (.5 if not winner else float(winner == game['candidate_color']))
        count += 1
    if manifest:
        assert roots == set(manifest['training_root_keys'])
    return {'games': count, 'legal_generated_moves': plies, 'failures': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--expected-games', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--training-manifest', type=Path)
    args = parser.parse_args()
    result = audit(args.raw, args.training_manifest)
    assert result['games'] == args.expected_games
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
