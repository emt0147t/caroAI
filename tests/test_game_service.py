from contextlib import contextmanager

import pytest

from app.db.repository import InMemoryGameRepository
from app.domain.game_rules import InvalidMoveError
from app.domain.game_state import GameMode, GameStatus, Player
from app.services import game_service as game_service_module
from app.services.game_service import (
    GameNotFoundError,
    GameService,
    GameStateChangedError,
)


def test_create_game():
    service = GameService(InMemoryGameRepository())

    game_id = service.create_game(GameMode.HUMAN_VS_AI)

    state = service.get_game(game_id)

    assert game_id
    assert state.mode == GameMode.HUMAN_VS_AI
    assert state.current_player == Player.X
    assert state.status == GameStatus.IN_PROGRESS
    assert state.move_count == 0


def test_get_nonexistent_game():
    service = GameService(InMemoryGameRepository())

    with pytest.raises(GameNotFoundError):
        service.get_game("does-not-exist")


def test_make_move():
    service = GameService(InMemoryGameRepository())

    game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    move = service.make_move(game_id, 7, 7)
    state = service.get_game(game_id)

    assert move.player == Player.X
    assert move.move_number == 1
    assert state.board[7][7] == "X"
    assert state.current_player == Player.O
    assert state.move_count == 1


def test_make_invalid_move():
    service = GameService(InMemoryGameRepository())

    game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    service.make_move(game_id, 7, 7)

    with pytest.raises(InvalidMoveError):
        service.make_move(game_id, 7, 7)


def test_service_keeps_games_isolated():
    service = GameService(InMemoryGameRepository())
    first_id = service.create_game(GameMode.HUMAN_VS_HUMAN)
    second_id = service.create_game(GameMode.HUMAN_VS_AI)

    service.make_move(first_id, 3, 4)

    assert service.get_game(first_id).board[3][4] == "X"
    assert service.get_game(second_id).board[3][4] == "EMPTY"
    assert service.get_game(second_id).move_count == 0


class TrackingInMemoryGameRepository(InMemoryGameRepository):
    """Expose whether a service transaction is still open during AI search."""

    def __init__(self):
        super().__init__()
        self.active_transactions = 0

    @contextmanager
    def transaction(self):
        with super().transaction() as uow:
            self.active_transactions += 1
            try:
                yield uow
            finally:
                self.active_transactions -= 1


def test_ai_search_runs_outside_write_transaction_and_rejects_stale_snapshot(
    monkeypatch,
):
    repository = TrackingInMemoryGameRepository()
    service = GameService(repository)
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    def concurrent_move_during_search(board, ai_player, difficulty):
        # This is a direct transaction-boundary assertion, not just a
        # same-thread RLock re-entry test: no UoW may be open during Minimax.
        assert repository.active_transactions == 0
        service.make_move(game_id, 8, 8)
        assert repository.active_transactions == 0
        return {"row": 6, "col": 8, "score": 0, "elapsed_ms": 1.0}

    monkeypatch.setattr(
        game_service_module, "run_ai_engine", concurrent_move_during_search
    )

    with pytest.raises(GameStateChangedError, match="state changed"):
        service.make_ai_move(game_id, "medium")

    state = service.get_game(game_id)
    assert repository.active_transactions == 0
    assert state.move_count == 2
    assert state.board[7][7] == "X"
    assert state.board[8][8] == "O"
    assert state.board[6][8] == "EMPTY"
    assert state.current_player == Player.X


def test_medium_search_is_not_blocked_by_impossible_admission_guard(monkeypatch):
    from app.ai.admission import ImpossibleAdmissionGuard

    guard = ImpossibleAdmissionGuard(max_concurrency=1, queue_wait_ms=0)
    repository = InMemoryGameRepository()
    service = GameService(repository, impossible_guard=guard)
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    def fake_medium_move(board, ai_player, difficulty):
        assert difficulty == "medium"
        return {"row": 6, "col": 8, "score": 0, "elapsed_ms": 1.0}

    monkeypatch.setattr(
        game_service_module, "run_ai_engine", fake_medium_move
    )

    with guard.acquire():
        move = service.make_ai_move(game_id, "medium")

    state = service.get_game(game_id)
    assert move.player == Player.O
    assert (move.row, move.col) == (6, 8)
    assert state.move_count == 2
    assert state.board[6][8] == "O"
