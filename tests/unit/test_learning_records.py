"""Reject fabricated histories and unsafe export selections before training."""
from copy import deepcopy

import pytest

from benchmarks.learning.records import board_key, validate_game
from benchmarks.learning.records import private_output
from pathlib import Path


def complete_game():
    coordinates = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2),
                   (1, 2), (0, 3), (1, 3), (0, 4)]
    return {'result': 'X_WON', 'move_count': 9,
            'moves': [{'ply': i + 1, 'player': i % 2 + 1, 'row': r, 'col': c}
                      for i, (r, c) in enumerate(coordinates)]}


def test_full_history_reconstructs_every_pre_move_board():
    game = complete_game()
    before = deepcopy(game)
    positions = validate_game(game)
    assert len(positions) == 9
    assert positions[0][0] == [[0] * 15 for _ in range(15)]
    assert positions[-1][0][0][:5] == [1, 1, 1, 1, 0]
    assert game == before


@pytest.mark.parametrize('kind', ['missing', 'truncated', 'order', 'player', 'result', 'count', 'occupied', 'bool'])
def test_bad_histories_cannot_become_training_data(kind):
    game = complete_game()
    if kind == 'missing':
        del game['moves']
    elif kind == 'truncated':
        game['moves'].pop()
    elif kind == 'order':
        game['moves'][2]['ply'] = 9
    elif kind == 'player':
        game['moves'][2]['player'] = 2
    elif kind == 'result':
        game['result'] = 'O_WON'
    elif kind == 'count':
        game['move_count'] = 10
    elif kind == 'occupied':
        game['moves'][2]['col'] = 0
    else:
        game['moves'][0]['row'] = False
    with pytest.raises(ValueError):
        validate_game(game)


def test_canonical_positions_group_d4_but_preserve_player_and_colors():
    board = [[0] * 15 for _ in range(15)]
    board[3][4], board[4][5] = 1, 2
    rotated = [list(row) for row in zip(*board[::-1])]
    assert board_key(board, 1) == board_key(rotated, 1)
    assert board_key(board, 1) != board_key(board, 2)


def test_private_outputs_reject_public_checkout_destinations(tmp_path):
    root = Path(__file__).resolve().parents[2]
    with pytest.raises(ValueError, match='Private results'):
        private_output(root / 'reports/private-history.json')
    assert private_output(tmp_path / 'private/result.json') == tmp_path / 'private/result.json'
