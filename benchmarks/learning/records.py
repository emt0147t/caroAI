"""Strict full-history replay and canonical board identities for offline data."""
import hashlib
import json
from pathlib import Path

from app.domain.game_rules import GameRules
from app.domain.game_state import GameMode, GameState, Player
from benchmarks.competitive.corpus import transform_cell


def private_output(path):
    """Keep owner-provided histories out of the proposed public source tree."""
    root = Path(__file__).resolve().parents[2]
    path = Path(path).resolve()
    if path.is_relative_to(root) and not path.is_relative_to(root / 'work'):
        raise ValueError('Private results must be outside this checkout or under ignored work/private/')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def numeric_board(state):
    return [[{'EMPTY': 0, 'X': 1, 'O': 2}[v] for v in row] for row in state.board]


def board_key(board, player):
    variants = []
    for rotation in range(4):
        for reflect in range(2):
            stones = sorted((value, *transform_cell((r, c), rotation, reflect))
                            for r, row in enumerate(board) for c, value in enumerate(row) if value)
            variants.append((player, tuple(stones)))
    return hashlib.sha256(repr(min(variants)).encode()).hexdigest()


def validate_game(game):
    """Fail closed on missing, truncated, unordered, illegal or nonterminal data."""
    if not isinstance(game.get('moves'), list) or not game['moves']:
        raise ValueError('Ordered complete moves are required; a final board is insufficient')
    state = GameState(mode=GameMode(game.get('mode', 'HUMAN_VS_AI')))
    positions = []
    for ply, move in enumerate(game['moves'], 1):
        player = 1 if state.current_player == Player.X else 2
        if (type(move.get('ply')) is not int or move['ply'] != ply
                or type(move.get('player')) is not int or move['player'] != player):
            raise ValueError('Moves must be contiguous and alternate players')
        if any(type(move.get(k)) is not int for k in ('row', 'col')):
            raise ValueError('Move coordinates must be integers')
        positions.append((numeric_board(state), player, (move['row'], move['col'])))
        GameRules.apply_move(state, move['row'], move['col'])
    if state.status.value not in ('X_WON', 'O_WON', 'DRAW') or state.status.value != game.get('result'):
        raise ValueError('Complete history does not match the declared terminal result')
    if 'move_count' in game and game['move_count'] != state.move_count:
        raise ValueError('Move count does not match the ordered history')
    return positions


def load_games(path):
    data = json.loads(path.read_text())
    if data.get('schema_version') != 1 or not isinstance(data.get('games'), list):
        raise ValueError('Unsupported dataset schema')
    for game in data['games']:
        validate_game(game)
    ids = [g['game_id'] for g in data['games']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate games are not independent examples')
    return data
