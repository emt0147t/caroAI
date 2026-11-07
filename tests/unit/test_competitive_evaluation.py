"""Validate specifications and experiment accounting without candidate code."""
import pytest

from benchmarks.competitive.corpus import base_cases, cases, fork_moves, wins
from benchmarks.competitive.metrics import paired_interval, percentile, wilson
from benchmarks.competitive.tournament import opening


@pytest.mark.parametrize('case', base_cases(), ids=lambda c: c.name)
def test_tactical_specifications_against_independent_domain_oracle(case):
    board = case.board()
    if case.outcome == 'win_now':
        assert wins(board, case.player) == set(case.expected_moves)
    elif case.outcome == 'block_unique':
        assert not wins(board, case.player)
        assert wins(board, 3 - case.player) == set(case.expected_moves)
    elif case.outcome == 'create_fork':
        assert not wins(board, case.player)
        assert fork_moves(board, case.player) == set(case.expected_moves)
    else:
        assert fork_moves(board, 3 - case.player)
        for row, col in case.expected_moves:
            board[row][col] = case.player
            assert not fork_moves(board, 3 - case.player)
            board[row][col] = 0


def test_symmetry_and_color_expansion_keeps_explicit_empty_answer_sets():
    expanded = list(cases())
    assert len(expanded) == 192
    assert len({c.name for c in expanded}) == len(expanded)
    for case in expanded:
        board = case.board()
        assert case.expected_moves
        assert all(board[r][c] == 0 for r, c in case.expected_moves)


def test_intervals_cover_known_counts_and_pairing():
    assert wilson(0, 0) is None
    assert wilson(100, 200)[0] < .5 < wilson(100, 200)[1]
    assert wilson(0, 200)[1] < .02
    assert paired_interval([.5] * 100) == [.5, .5]
    assert paired_interval([0, 1] * 50)[0] < .5 < paired_interval([0, 1] * 50)[1]
    assert percentile([1, 2, 3, 4, 5], .95) == 5


def test_opening_protocol_is_seeded_and_varied():
    assert opening(77) == opening(77)
    assert len({tuple(opening(seed)) for seed in range(100)}) >= 80
    assert all(len(set(opening(seed))) == len(opening(seed)) for seed in range(100))
