"""Verify downloaded artifact hashes and replay all tournament logs from game rules.

Run: python -m reports.competitive.replay_artifacts --archives /path/to/id-named-zips
The companion artifact-manifest.json pins archive IDs and SHA-256 digests.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from app.domain.game_rules import GameRules
from app.domain.game_state import GameState, Player


def replay(game):
    state = GameState()
    for move in game['opening']:
        GameRules.apply_move(state, *move)
    for record in game['moves']:
        assert record['player'] == (1 if state.current_player == Player.X else 2)
        GameRules.apply_move(state, *record['move'])
    winner = 1 if state.winner == Player.X else 2 if state.winner == Player.O else 0
    assert state.status.value in {'X_WON', 'O_WON', 'DRAW'}
    assert state.status.value == game['terminal']
    assert winner == game['winner']
    score = .5 if winner == 0 else float(winner == game['candidate_color'])
    assert score == game['candidate_score']
    return score, len(game['moves'])


def verify(manifest, archives):
    count = moves = 0
    for artifact in manifest['artifacts']:
        path = archives / (str(artifact['id']) + '.zip')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact['archive_sha256']
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith('.jsonl') or name.startswith(('engine', 'server')):
                    continue
                games = [json.loads(line) for line in archive.read(name).splitlines()]
                summary = json.loads(archive.read(name[:-1]))
                assert len(games) == summary['games']
                points = 0
                for game in games:
                    score, plies = replay(game)
                    points += score
                    moves += plies
                assert points / len(games) == summary['score_rate']
                count += len(games)
    return {'source_sha': manifest['source_sha'], 'complete_games': count,
            'legal_logged_moves': moves, 'failures': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('artifact-manifest.json'))
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.manifest.read_text()), args.archives), indent=2))
