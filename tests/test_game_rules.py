import pytest

from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, GameStatus, Player


def test_initial_state():
    state = GameState(mode=GameMode.HUMAN_VS_AI)

    assert state.current_player == Player.X
    assert state.status == GameStatus.IN_PROGRESS
    assert state.move_count == 0
    assert state.winner is None
    assert len(state.board) == 15
    assert len(state.board[0]) == 15


def test_valid_move_changes_state():
    state = GameState()

    move = GameRules.apply_move(state, 7, 7)

    assert move.player == Player.X
    assert move.move_number == 1
    assert state.board[7][7] == "X"
    assert state.current_player == Player.O
    assert state.move_count == 1


def test_cannot_play_occupied_cell():
    state = GameState()

    GameRules.apply_move(state, 7, 7)

    with pytest.raises(InvalidMoveError, match="already occupied"):
        GameRules.apply_move(state, 7, 7)


def test_horizontal_win():
    state = GameState()

    for col in range(5):
        state.board[7][col] = "X"

    assert GameRules.has_won(state, 7, 4, Player.X)


def test_vertical_win():
    state = GameState()

    for row in range(5):
        state.board[row][7] = "O"

    assert GameRules.has_won(state, 4, 7, Player.O)


def test_diagonal_win():
    state = GameState()

    for i in range(5):
        state.board[i][i] = "X"

    assert GameRules.has_won(state, 4, 4, Player.X)


def test_game_ends_after_win():
    state = GameState()

    GameRules.apply_move(state, 0, 0)
    GameRules.apply_move(state, 1, 0)
    GameRules.apply_move(state, 0, 1)
    GameRules.apply_move(state, 1, 1)
    GameRules.apply_move(state, 0, 2)
    GameRules.apply_move(state, 1, 2)
    GameRules.apply_move(state, 0, 3)
    GameRules.apply_move(state, 1, 3)
    GameRules.apply_move(state, 0, 4)

    assert state.status == GameStatus.X_WON
    assert state.winner == Player.X


def test_cannot_move_after_game_finished():
    state = GameState()

    GameRules.apply_move(state, 0, 0)
    GameRules.apply_move(state, 1, 0)
    GameRules.apply_move(state, 0, 1)
    GameRules.apply_move(state, 1, 1)
    GameRules.apply_move(state, 0, 2)
    GameRules.apply_move(state, 1, 2)
    GameRules.apply_move(state, 0, 3)
    GameRules.apply_move(state, 1, 3)
    GameRules.apply_move(state, 0, 4)

    with pytest.raises(InvalidMoveError, match="already finished"):
        GameRules.apply_move(state, 2, 2)