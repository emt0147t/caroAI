"""Public engine integration preserves contracts and explicit budget precedence."""
import pytest

from app.ai import engine


def board():
    result = [[0] * 15 for _ in range(15)]
    result[7][7] = 1
    return result


@pytest.mark.parametrize('level', ['EASY', 'MEDIUM', 'unknown', ''])
def test_legacy_routes_are_preserved(monkeypatch, level):
    captured = {}

    def legacy(**kwargs):
        captured.update(kwargs)
        return (7, 8), 123

    monkeypatch.setattr(engine, 'find_best_move', legacy)
    monkeypatch.setattr(engine, 'choose_move', lambda *args, **kwargs: pytest.fail('unexpected competitive route'))
    result = engine.get_ai_move(board(), 2, level, collect_stats=False)
    assert captured['depth'] == (1 if level == 'EASY' else 2)
    assert set(result) == {'row', 'col', 'score', 'elapsed_ms'}


@pytest.mark.parametrize('level', ['HARD', 'IMPOSSIBLE'])
def test_strong_routes_keep_move_validation_and_collect_stats_contract(monkeypatch, level):
    captured = {}

    def search(board, player, policy, *, time_budget_ms):
        captured.update(policy=policy, budget=time_budget_ms)
        return {'row': 7, 'col': 8, 'score': 100, 'search_stats': {'depth': 1, 'search_ms': 1}}

    monkeypatch.setattr(engine, 'choose_move', search)
    result = engine.get_ai_move(board(), 2, level, collect_stats=False, time_budget_ms=5.5)
    assert captured['budget'] == 5.5
    assert set(result) == {'row', 'col', 'score', 'elapsed_ms'}
    monkeypatch.setattr(engine, 'choose_move', lambda *a, **k: {'row': 7, 'col': 7, 'score': 0})
    with pytest.raises(ValueError, match='occupied'):
        engine.get_ai_move(board(), 2, level)


def test_environment_budget_override_and_explicit_argument_precedence(monkeypatch):
    monkeypatch.setenv('CAROAI_IMPOSSIBLE_TIME_BUDGET_MS', '0')
    result = engine.get_ai_move(board(), 2, 'impossible')
    assert result['search_stats']['budget_ms'] == 0
    assert result['search_stats']['timed_out']
    result = engine.get_ai_move(board(), 2, 'impossible', time_budget_ms=5)
    assert result['search_stats']['budget_ms'] == 5
    monkeypatch.setenv('CAROAI_IMPOSSIBLE_TIME_BUDGET_MS', 'bad')
    with pytest.raises(ValueError, match='must be numeric'):
        engine.get_ai_move(board(), 2, 'impossible')


@pytest.mark.parametrize('value', ['nan', 'inf', '-1'])
def test_invalid_environment_budget_fails_closed(monkeypatch, value):
    monkeypatch.setenv('CAROAI_IMPOSSIBLE_TIME_BUDGET_MS', value)
    with pytest.raises(ValueError):
        engine.get_ai_move(board(), 2, 'IMPOSSIBLE')
