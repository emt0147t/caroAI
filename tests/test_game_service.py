import pytest

from app.domain.game_rules import InvalidMoveError
from app.domain.game_state import GameMode, GameStatus, Player
from app.services.game_service import GameNotFoundError, GameService


def test_create_game():
    service = GameService()

    game_id = service.create_game(GameMode.HUMAN_VS_AI)

    state = service.get_game(game_id)

    assert game_id
    assert state.mode == GameMode.HUMAN_VS_AI
    assert state.current_player == Player.X
    assert state.status == GameStatus.IN_PROGRESS
    assert state.move_count == 0


def test_get_nonexistent_game():
    service = GameService()

    with pytest.raises(GameNotFoundError):
        service.get_game("does-not-exist")


def test_make_move():
    service = GameService()

    game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    move = service.make_move(game_id, 7, 7)
    state = service.get_game(game_id)

    assert move.player == Player.X
    assert move.move_number == 1
    assert state.board[7][7] == "X"
    assert state.current_player == Player.O
    assert state.move_count == 1


def test_make_invalid_move():
    service = GameService()

    game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    service.make_move(game_id, 7, 7)

    with pytest.raises(InvalidMoveError):
        service.make_move(game_id, 7, 7)


def test_service_keeps_games_isolated():
    service = GameService()
    first_id = service.create_game(GameMode.HUMAN_VS_HUMAN)
    second_id = service.create_game(GameMode.HUMAN_VS_AI)

    service.make_move(first_id, 3, 4)

    assert service.get_game(first_id).board[3][4] == "X"
    assert service.get_game(second_id).board[3][4] == "EMPTY"
    assert service.get_game(second_id).move_count == 0
