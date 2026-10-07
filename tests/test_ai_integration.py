import pytest

from app.ai.adapter import board_from_ai, board_to_ai
from app.domain.game_state import BOARD_SIZE, GameMode, Player
from app.services import game_service as game_service_module
from app.services.game_service import GameService, InvalidAIMoveError


def create_backend_board():
    return [
        ["EMPTY" for _ in range(BOARD_SIZE)]
        for _ in range(BOARD_SIZE)
    ]


def test_board_adapter_maps_backend_values_in_both_directions():
    backend = create_backend_board()
    backend[0][0] = "X"
    backend[7][7] = "O"

    ai_board = board_to_ai(backend)

    assert ai_board[0][0] == 1
    assert ai_board[7][7] == 2
    assert ai_board[0][1] == 0

    round_tripped = board_from_ai(ai_board)

    assert round_tripped == backend
    assert round_tripped is not backend
    assert ai_board is not backend


def test_board_adapter_rejects_invalid_shape():
    with pytest.raises(ValueError, match="15x15"):
        board_to_ai([["EMPTY"]])


def test_ai_service_uses_snapshot_and_backend_applies_result(monkeypatch):
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    captured = {}

    def fake_ai_move(board, ai_player, difficulty):
        captured["board"] = board
        captured["ai_player"] = ai_player
        captured["difficulty"] = difficulty
        board[0][0] = 2
        return {
            "row": 6,
            "col": 8,
            "score": 10,
            "elapsed_ms": 1.5,
        }

    monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)

    move = service.make_ai_move(game_id, "medium")
    state = service.get_game(game_id)

    assert captured["ai_player"] == 2
    assert captured["difficulty"] == "medium"
    assert captured["board"][7][7] == 1
    assert state.board[0][0] == "EMPTY"
    assert state.board[6][8] == "O"
    assert move.player.value == "O"
    assert move.move_number == 2
    assert state.current_player.value == "X"


def test_ai_service_rejects_illegal_ai_move(monkeypatch):
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    def fake_ai_move(board, ai_player, difficulty):
        return {"row": 7, "col": 7, "score": 0, "elapsed_ms": 1.0}

    monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)

    with pytest.raises(InvalidAIMoveError, match="already occupied"):
        service.make_ai_move(game_id, "easy")

    state = service.get_game(game_id)
    assert state.board[7][7] == "X"
    assert state.move_count == 1


def test_ai_service_rejects_invalid_difficulty(monkeypatch):
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    def fail_if_called(*args, **kwargs):
        pytest.fail("AI engine must not run for an invalid difficulty")

    monkeypatch.setattr(game_service_module, "run_ai_engine", fail_if_called)

    with pytest.raises(InvalidAIMoveError, match="easy, medium, hard"):
        service.make_ai_move(game_id, "impossible")


def test_ai_service_requires_human_vs_ai_mode():
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    with pytest.raises(InvalidAIMoveError, match="HUMAN_VS_AI"):
        service.make_ai_move(game_id, "medium")


def test_ai_service_requires_ai_turn():
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)

    with pytest.raises(InvalidAIMoveError, match="not the AI turn"):
        service.make_ai_move(game_id, "medium")


def _prepare_ai_turn(service, mode=GameMode.HUMAN_VS_AI):
    game_id = service.create_game(mode)
    state = service.get_game(game_id)
    return game_id, state


def test_ai_service_applies_winning_move_and_marks_o_won(monkeypatch):
    service = GameService()
    game_id, state = _prepare_ai_turn(service)

    state.board[7][7:11] = ["O", "O", "O", "O"]
    state.move_count = 4
    state.current_player = Player.O

    def fake_ai_move(board, ai_player, difficulty):
        return {"row": 7, "col": 11, "score": 100000000, "elapsed_ms": 1.0}

    monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)

    move = service.make_ai_move(game_id, "medium")
    state = service.get_game(game_id)

    assert move.player.value == "O"
    assert (move.row, move.col) == (7, 11)
    assert state.status.value == "O_WON"
    assert state.winner.value == "O"
    assert state.current_player.value == "O"


def test_ai_service_applies_blocking_move(monkeypatch):
    service = GameService()
    game_id, state = _prepare_ai_turn(service)

    state.board[7][7:11] = ["X", "X", "X", "X"]
    state.move_count = 4
    state.current_player = __import__("app.domain.game_state", fromlist=["Player"]).Player.O

    def fake_ai_move(board, ai_player, difficulty):
        return {"row": 7, "col": 11, "score": 0, "elapsed_ms": 1.0}

    monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)

    move = service.make_ai_move(game_id, "hard")
    state = service.get_game(game_id)

    assert move.player.value == "O"
    assert (move.row, move.col) == (7, 11)
    assert state.board[7][11] == "O"
    assert state.status.value == "IN_PROGRESS"
    assert state.winner is None


@pytest.mark.parametrize(
    "ai_result",
    [
        None,
        {"row": 7},
        {"col": 7},
        {"row": 7.0, "col": 7},
        {"row": True, "col": 7},
        {"row": 7, "col": False},
    ],
)
def test_ai_service_rejects_malformed_ai_output(monkeypatch, ai_result):
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    monkeypatch.setattr(
        game_service_module,
        "run_ai_engine",
        lambda board, ai_player, difficulty: ai_result,
    )

    with pytest.raises(InvalidAIMoveError, match="invalid"):
        service.make_ai_move(game_id, "medium")


@pytest.mark.parametrize(
    "ai_result",
    [
        {"row": -1, "col": 7},
        {"row": 15, "col": 7},
        {"row": 7, "col": -1},
        {"row": 7, "col": 15},
    ],
)
def test_ai_service_rejects_out_of_bounds_ai_move(monkeypatch, ai_result):
    service = GameService()
    game_id = service.create_game(GameMode.HUMAN_VS_AI)
    service.make_move(game_id, 7, 7)

    monkeypatch.setattr(
        game_service_module,
        "run_ai_engine",
        lambda board, ai_player, difficulty: ai_result,
    )

    with pytest.raises(InvalidAIMoveError, match="illegal"):
        service.make_ai_move(game_id, "medium")
