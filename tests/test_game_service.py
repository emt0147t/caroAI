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


def test_ai_search_runs_outside_write_transaction_and_rejects_stale_snapshot(
    monkeypatch,
):
    service = GameService(InMemoryGameRepository())
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    def concurrent_move_during_search(board, ai_player, difficulty):
        # This mutation can commit only if the AI calculation is not holding
        # the repository transaction/lock while the engine is running.
        service.make_move(game_id, 8, 8)
        return {"row": 6, "col": 8, "score": 0, "elapsed_ms": 1.0}

    monkeypatch.setattr(
        game_service_module, "run_ai_engine", concurrent_move_during_search
    )

    with pytest.raises(GameStateChangedError, match="state changed"):
        service.make_ai_move(game_id, "medium")

    state = service.get_game(game_id)
    assert state.move_count == 2
    assert state.board[7][7] == "X"
    assert state.board[8][8] == "O"
    assert state.board[6][8] == "EMPTY"
    assert state.current_player == Player.X
