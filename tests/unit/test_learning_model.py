"""Learning math, artifact safety, symmetric features and interrupted state."""
from dataclasses import replace
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from app.ai.competitive import Context, Exhausted, POLICIES, Position
from benchmarks.learning.model import Model, action_features, probabilities
from benchmarks.learning.search import choose, ranked_roots, root_iteration
from benchmarks.learning.train import episode, update


def quiet_board():
    board = [[0] * 15 for _ in range(15)]
    board[7][7], board[7][8] = 1, 2
    return board


def test_model_roundtrip_and_schema_checks(tmp_path):
    path = tmp_path / 'model.json'
    model = Model()
    model.save(path)
    assert Model.load(path).digest() == model.digest()
    for weights in ([1], [float('nan')] * 8, [float('inf')] * 8, [21] * 8):
        doc = model.document()
        doc['policy_weights'] = weights
        path.write_text(json.dumps(doc))
        with pytest.raises(ValueError):
            Model.load(path)


def test_relative_features_are_color_invariant_and_restore_position():
    pos = Position(quiet_board())
    before = [row[:] for row in pos.board], pos.stones[:], pos.occupied, pos.raw
    features, value = action_features(pos, 1, (6, 7))
    other = [[3 - p if p else 0 for p in row] for row in quiet_board()]
    swapped, other_value = action_features(Position(other), 2, (6, 7))
    assert np.array_equal(features, swapped) and np.array_equal(value, other_value)
    assert (pos.board, pos.stones, pos.occupied, pos.raw) == before


def test_policy_gradient_rewards_chosen_action_and_penalizes_losing_action():
    for reward, direction in ((1, 1), (2, -1)):
        model = Model(policy=np.zeros(8), value=np.zeros(7))
        gradient = np.array([0, 1, 0, 0, 0, 0, 0, 0], dtype=float)
        update(model, [([(1, np.ones(7), gradient, 0)], {'winner': reward})], .1)
        assert np.sign(model.policy[1]) == direction
        assert np.sign(model.predict(np.ones(7))) == direction


def test_probability_stability_and_temperature_validation():
    p = probabilities([10000, -10000, 10000])
    assert np.isfinite(p).all() and abs(sum(p) - 1) < 1e-12
    for temperature in (0, -1, float('nan'), float('inf')):
        with pytest.raises(ValueError):
            probabilities([0, 1], temperature)


def test_selfplay_is_complete_deterministic_and_changes_both_heads():
    model = Model()
    first = episode(model, np.random.default_rng(72), 20280002, .7)
    second = episode(model, np.random.default_rng(72), 20280002, .7)
    assert first[1] == second[1]
    assert first[1]['terminal'] in ('X_WON', 'O_WON', 'DRAW')
    policy, value = model.policy.copy(), model.value.copy()
    update(model, [first], .1)
    assert not np.array_equal(policy, model.policy)
    assert not np.array_equal(value, model.value)


def test_zero_budget_preserves_exact_win_and_unique_block_without_model_override():
    model = Model(policy=np.full(8, -10))
    for player in (1, 2):
        board = [[0] * 15 for _ in range(15)]
        board[7][2] = 3 - player
        board[7][3:7] = [player] * 4
        for side in (player, 3 - player):
            result = choose(board, side, 'IMPOSSIBLE', 0, model)
            assert (result['row'], result['col']) == (7, 7)
            assert result['search_stats']['fallback_used'] is False


def test_interrupted_root_restores_raw_and_bitboard_state():
    from time import perf_counter
    pos = Position(quiet_board())
    policy = replace(POLICIES['HARD'], node_limit=1)
    context = Context(policy, perf_counter() + 10)
    before = [row[:] for row in pos.board], pos.stones[:], pos.occupied, pos.raw
    moves, _ = ranked_roots(pos, 1, context, Model())
    with pytest.raises(Exhausted):
        root_iteration(pos, 1, moves, 4, context)
    assert (pos.board, pos.stones, pos.occupied, pos.raw) == before


def test_concurrent_requests_have_private_state_and_legal_moves():
    board = quiet_board()
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda _: choose(board, 1, 'HARD', 20, Model()), range(8)))
    assert board == quiet_board()
    assert all(board[r['row']][r['col']] == 0 for r in results)


def test_known_source_models_are_offline_only():
    root = Path(__file__).resolve().parents[2]
    for path in (root / 'app').rglob('*.py'):
        assert 'benchmarks.learning' not in path.read_text()
