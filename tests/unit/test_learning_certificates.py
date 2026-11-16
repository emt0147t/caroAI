"""Public synthetic proofs; real production histories stay owner-controlled."""
import pytest

from benchmarks.competitive.corpus import base_cases
from benchmarks.learning.certificates import prove, verify_certificate
from benchmarks.learning.witness import prove_plan, verify_plan


@pytest.mark.parametrize('case', [c for c in base_cases() if c.outcome.startswith('vcf_')], ids=lambda c: c.name)
def test_vcf_proofs_have_independent_complete_certificates(case):
    result = prove(case.board(), case.player, int(case.outcome[-1]))
    assert result.status == 'PROVEN'
    assert verify_certificate(case.board(), case.player, result.line)


def test_exhaustion_is_not_reported_as_refutation_or_safety():
    assert prove([[0] * 15 for _ in range(15)], 1, 3, max_nodes=0).status == 'UNKNOWN'


def test_composed_crossing_threes_win_against_every_reply():
    # A composed legal eight-stone setup, unrelated to production game data.
    board = [[0] * 15 for _ in range(15)]
    for r, c in ((7, 5), (7, 6), (5, 7), (6, 7)):
        board[r][c] = 1
    for r, c in ((0, 0), (0, 5), (5, 0), (14, 14)):
        board[r][c] = 2
    status, certificate = prove_plan(board, 1, [(7, 7)])
    assert status == 'PROVEN'
    assert certificate['kind'] == 'all_replies'
    assert verify_plan(board, 1, certificate)
    # Occupying the demonstrated square refutes this plan, not all play.
    board[7][7] = 2
    assert prove_plan(board, 1, [(7, 7)])[0] == 'NO_PROOF'
