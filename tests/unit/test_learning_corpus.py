"""Synthetic fixtures for the private-corpus CLI; no production records."""
from copy import deepcopy

import pytest

from benchmarks.learning.build_corpus import build
from benchmarks.learning.witness import prove_plan


def synthetic_report():
    board = [[0] * 15 for _ in range(15)]
    for r, c in ((7, 5), (7, 6), (5, 7), (6, 7)):
        board[r][c] = 1
    for r, c in ((0, 0), (0, 5), (5, 0)):
        board[r][c] = 2
    after = deepcopy(board)
    after[14][14] = 2
    status, certificate = prove_plan(after, 1, [(7, 7)])
    assert status == 'PROVEN'
    finding = {'board': board, 'player': 2, 'actual_move': [14, 14], 'ply': 8,
               'observed_human_plan': [[7, 7]], 'expected_moves': [[7, 7]],
               'forcing_attack_depth': 3, 'expected_scope': 'Refutes synthetic fixed plan only.',
               'unknown_alternatives': 0, 'certificate': certificate}
    return {'games': [{'game_id': 'synthetic-test-record', 'first_observed_plan_error': finding}]}


def test_corpus_rechecks_oracles_and_uses_opaque_case_names():
    result = build(synthetic_report())
    assert len(result['cases']) == 1
    assert result['cases'][0]['name'] == 'private-case-1'
    assert result['cases'][0]['source_game_fingerprint'] != 'synthetic-test-record'


@pytest.mark.parametrize('kind', ['empty', 'unknown', 'occupied'])
def test_uncertified_or_invalid_expected_sets_are_rejected(kind):
    report = synthetic_report()
    finding = report['games'][0]['first_observed_plan_error']
    if kind == 'empty':
        finding['expected_moves'] = []
    elif kind == 'unknown':
        finding['unknown_alternatives'] = 1
    else:
        finding['expected_moves'] = [[7, 5]]
    with pytest.raises(ValueError):
        build(report)
