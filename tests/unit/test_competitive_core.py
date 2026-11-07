"""Independent tactical oracles and cache/state/deadline regression tests."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import random
from time import perf_counter

import pytest

from app.ai.competitive import (
    Context, Exhausted, INF, LOWER, POLICIES, Position, UPPER,
    _ordered, _prove_four, _root, _search, choose_move,
)
from app.ai.threats import cells, encode, fork_moves, winning_cells
from benchmarks.competitive.corpus import base_cases, cases, fork_moves as oracle_forks, wins


@pytest.mark.parametrize('level', ['HARD', 'IMPOSSIBLE'])
@pytest.mark.parametrize('case', list(cases()), ids=lambda case: case.name)
def test_tactical_answer_sets_and_input_integrity(case, level):
    board = case.board()
    original = [row[:] for row in board]
    result = choose_move(board, case.player, POLICIES[level])
    assert (result['row'], result['col']) in case.expected_moves
    assert board == original
    assert result['elapsed_ms'] < POLICIES[level].time_ms + 150


def test_bitboard_wins_match_domain_oracle_randomized_and_edges():
    rng = random.Random(6207)
    for _ in range(150):
        board = [[0] * 15 for _ in range(15)]
        for index in rng.sample(range(225), rng.randrange(4, 180)):
            board[index // 15][index % 15] = rng.choice((1, 2))
        stones = encode(board)
        for player in (1, 2):
            actual = set(cells(winning_cells(stones[player], stones[1] | stones[2])))
            assert actual == wins(board, player)


@pytest.mark.parametrize('case', [case for case in base_cases() if case.outcome == 'create_fork'])
def test_exact_forks_match_independent_bruteforce(case):
    board = case.board()
    stones = encode(board)
    actual = set(cells(fork_moves(stones[case.player], stones[1] | stones[2])))
    assert actual == oracle_forks(board, case.player)


def context(policy=None, use_tt=True):
    policy = policy or replace(POLICIES['HARD'], quiet_limit=3, node_limit=1000000)
    return Context(policy, perf_counter() + 30, use_tt=use_tt)


def test_tt_does_not_alias_extended_leaf_with_deeper_nominal_horizon():
    board = [[0] * 15 for _ in range(15)]
    for c in range(3, 7):
        board[7][c] = 1
    board[7][2] = 2
    for r in range(4, 7):
        board[r][7] = 2
    board[8][7] = 1
    pos = Position(board)
    warm = context()
    _search(pos, 2, 0, 1, -INF, INF, 3, warm)
    actual = _search(pos, 2, 1, 1, -INF, INF, 3, warm)
    expected = _search(pos, 2, 1, 1, -INF, INF, 3, context(use_tt=False))
    assert actual == expected
    assert {key[3:] for key in warm.table if key[:3] == (pos.stones[1], pos.stones[2], 2)} >= {(0, 1), (1, 1)}


def quiet_board():
    board = [[0] * 15 for _ in range(15)]
    board[7][7], board[7][8] = 1, 2
    return board


@pytest.mark.parametrize('window,bound', [('high', LOWER), ('low', UPPER)])
def test_tt_bounds_research_correctly_in_a_full_window(window, bound):
    pos = Position(quiet_board())
    expected = _search(pos, 1, 2, 1, -INF, INF, 0, context(use_tt=False))
    ctx = context()
    alpha, beta = (expected - 100, expected - 1) if window == 'high' else (expected + 1, expected + 100)
    _search(pos, 1, 2, 1, alpha, beta, 0, ctx)
    key = pos.stones[1], pos.stones[2], 1, 2, 1
    assert ctx.table[key].bound == bound
    assert _search(pos, 1, 2, 1, -INF, INF, 0, ctx) == expected
    assert ctx.tt_hits > 0


def test_fixed_depth_tt_on_off_scores_and_moves_are_identical():
    policy = replace(POLICIES['HARD'], depth=4, quiet_limit=3, extensions=1, time_ms=30000, node_limit=1000000)
    board = quiet_board()
    with_tt = choose_move(board, 1, policy, use_tt=True)
    without_tt = choose_move(board, 1, policy, use_tt=False)
    assert with_tt['search_stats']['depth'] == without_tt['search_stats']['depth'] == 4
    assert (with_tt['row'], with_tt['col'], with_tt['score']) == (
        without_tt['row'], without_tt['col'], without_tt['score'])


def test_tactical_membership_is_preserved_before_tt_promotion_and_quiet_cap():
    case = next(c for c in base_cases() if c.name == 'extend_open_three')
    pos = Position(case.board())
    policy = replace(POLICIES['HARD'], quiet_limit=1)
    first = _ordered(pos, 1, context(policy))
    second = _ordered(pos, 1, context(policy), tt_move=(0, 0))
    assert set(first) == set(second)
    assert set(case.expected_moves) <= set(first)
    assert len(first) > policy.quiet_limit


def test_timeout_restores_all_internal_search_state():
    pos = Position(quiet_board())
    before = [row[:] for row in pos.board], pos.stones[:], pos.occupied, pos.raw
    ctx = context(replace(POLICIES['HARD'], node_limit=1))
    with pytest.raises(Exhausted):
        _root(pos, 1, 4, ctx)
    assert (pos.board, pos.stones, pos.occupied, pos.raw) == before


def test_zero_budget_keeps_mandatory_tactics_and_reports_fallback():
    for case in base_cases():
        if case.outcome not in ('win_now', 'block_unique'):
            continue
        result = choose_move(case.board(), case.player, POLICIES['IMPOSSIBLE'], time_budget_ms=0)
        assert (result['row'], result['col']) in case.expected_moves
        assert result['search_stats']['fallback_used'] is False
    board = quiet_board()
    result = choose_move(board, 1, POLICIES['IMPOSSIBLE'], time_budget_ms=0)
    assert board[result['row']][result['col']] == 0
    assert result['search_stats']['fallback_used'] is True
    assert result['search_stats']['timed_out'] is True
    assert result['search_stats']['depth'] == 0


def test_deterministic_complete_search_and_concurrent_request_isolation():
    board = quiet_board()
    original = [row[:] for row in board]
    policy = replace(POLICIES['HARD'], depth=2, quiet_limit=3, time_ms=5000)
    with ThreadPoolExecutor(max_workers=4) as pool:
        outputs = list(pool.map(lambda _: choose_move(board, 1, policy), range(8)))
    assert len({(r['row'], r['col'], r['score']) for r in outputs}) == 1
    assert board == original
    for output in outputs:
        stats = output['search_stats']
        assert stats['generated_candidates'] >= stats['expanded_candidates'] > 0
        assert stats['leaves'] > 0


def chain_board():
    board = [[0] * 15 for _ in range(15)]
    for r, c in [(7, 4), (7, 5), (7, 6), (5, 5), (6, 6)]:
        board[r][c] = 1
    board[7][3] = 2
    return board


def test_continuous_four_chain_has_independent_forced_reply_certificate():
    board = chain_board()
    assert not oracle_forks(board, 1)
    board[7][7] = 1
    assert not wins(board, 2)
    assert wins(board, 1) == {(7, 8)}
    board[7][8] = 2
    board[8][8] = 1
    assert not wins(board, 2)
    assert wins(board, 1) == {(4, 4), (9, 9)}
    for level in ('HARD', 'IMPOSSIBLE'):
        result = choose_move(chain_board(), 1, POLICIES[level])
        assert (result['row'], result['col']) == (7, 7)
    assert result['search_stats']['shortcut'] == 'proven_four_chain'


def test_proof_does_not_ignore_a_defender_counter_win():
    board = chain_board()
    for c in range(4):
        board[0][c] = 2
    pos = Position(board)
    assert _prove_four(pos, 1, 5, 0, context()) is None
    result = choose_move(board, 1, POLICIES['IMPOSSIBLE'])
    assert (result['row'], result['col']) == (0, 4)


def test_two_distinct_opponent_wins_are_reported_as_forced_loss():
    board = [[0] * 15 for _ in range(15)]
    for c in range(4, 8):
        board[7][c] = 2
    result = choose_move(board, 1, POLICIES['HARD'])
    assert result['search_stats']['shortcut'] == 'forced_loss'
    assert result['score'] < -1000000
    assert (result['row'], result['col']) in {(7, 3), (7, 8)}


@pytest.mark.parametrize('budget', [-1, float('inf'), float('nan')])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValueError):
        choose_move(quiet_board(), 1, POLICIES['HARD'], time_budget_ms=budget)


def test_full_board_has_controlled_error():
    with pytest.raises(ValueError, match='No legal candidate'):
        choose_move([[1] * 15 for _ in range(15)], 2, POLICIES['HARD'])


def test_root_alpha_window_agrees_with_independent_full_window_enumeration():
    pos = Position(quiet_board())
    ctx = context()
    move, score = _root(pos, 1, 3, ctx)
    full = []
    reference = context(use_tt=False)
    for candidate in _ordered(pos, 1, reference):
        old = pos.play(candidate, 1)
        try:
            value = -_search(pos, 2, 2, reference.policy.extensions, -INF, INF, 1, reference)
            full.append((candidate, value))
        finally:
            pos.undo(candidate, 1, old)
    best = max(value for _, value in full)
    assert score == best
    assert move == next(candidate for candidate, value in full if value == best)
    assert ctx.stats.nodes <= reference.stats.nodes


def test_horizon_extension_searches_independently_verified_forcing_moves(monkeypatch):
    from app.ai import competitive
    case = next(c for c in base_cases() if c.name == 'extend_open_three')
    board = case.board()
    expected = set()
    for r in range(15):
        for c in range(15):
            if board[r][c]:
                continue
            board[r][c] = 1
            if wins(board, 1):
                expected.add((r, c))
            board[r][c] = 0
    generated = []
    original = competitive._ordered

    def capture(*args, **kwargs):
        moves = original(*args, **kwargs)
        generated.append(set(moves))
        return moves

    monkeypatch.setattr(competitive, '_ordered', capture)
    _search(Position(board), 1, 0, 1, -INF, INF, 0, context())
    assert generated[0] == expected
