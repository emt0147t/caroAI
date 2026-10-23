import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import game_service as game_service_module


client = TestClient(app)


def test_create_game():
    response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_HUMAN"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["mode"] == "HUMAN_VS_HUMAN"
    assert data["status"] == "IN_PROGRESS"
    assert data["current_player"] == "X"
    assert data["move_count"] == 0
    assert data["winner"] is None
    assert len(data["board"]) == 15
    assert all(len(row) == 15 for row in data["board"])


def test_make_first_move():
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_HUMAN"},
    )

    game_id = create_response.json()["id"]

    response = client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 7, "col": 7},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["move"]["row"] == 7
    assert data["move"]["col"] == 7
    assert data["move"]["player"] == "X"
    assert data["move"]["move_number"] == 1

    assert data["game"]["current_player"] == "O"
    assert data["game"]["move_count"] == 1


def test_cannot_make_move_on_occupied_cell():
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_HUMAN"},
    )

    game_id = create_response.json()["id"]

    client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 7, "col": 7},
    )

    response = client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 7, "col": 7},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cell is already occupied"


def test_invalid_coordinates():
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_HUMAN"},
    )

    game_id = create_response.json()["id"]

    response = client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 15, "col": 7},
    )

    assert response.status_code == 422


def test_ai_move_happy_path(monkeypatch):
    def fake_ai_move(board, ai_player, difficulty):
        assert ai_player == 2
        assert difficulty == "medium"
        assert board[7][7] == 1
        return {
            "row": 6,
            "col": 8,
            "score": 10,
            "elapsed_ms": 1.5,
        }

    monkeypatch.setattr(
        game_service_module,
        "run_ai_engine",
        fake_ai_move,
    )

    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_AI"},
    )
    game_id = create_response.json()["id"]

    human_response = client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 7, "col": 7},
    )
    assert human_response.status_code == 200
    assert human_response.json()["game"]["current_player"] == "O"

    response = client.post(
        f"/api/games/{game_id}/ai-move",
        json={"difficulty": "medium"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["move"] == {
        "row": 6,
        "col": 8,
        "player": "O",
        "move_number": 2,
    }
    assert data["game"]["board"][6][8] == "O"
    assert data["game"]["current_player"] == "X"
    assert data["game"]["move_count"] == 2


def test_ai_move_rejects_wrong_mode():
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_HUMAN"},
    )
    game_id = create_response.json()["id"]

    response = client.post(
        f"/api/games/{game_id}/ai-move",
        json={"difficulty": "medium"},
    )

    assert response.status_code == 400
    assert "HUMAN_VS_AI" in response.json()["detail"]


def test_ai_move_requires_ai_turn():
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_AI"},
    )
    game_id = create_response.json()["id"]

    response = client.post(
        f"/api/games/{game_id}/ai-move",
        json={"difficulty": "medium"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "It is not the AI turn"


def test_ai_move_rejects_illegal_ai_move(monkeypatch):
    def fake_ai_move(board, ai_player, difficulty):
        return {
            "row": 7,
            "col": 7,
            "score": 0,
            "elapsed_ms": 1.0,
        }

    monkeypatch.setattr(
        game_service_module,
        "run_ai_engine",
        fake_ai_move,
    )

    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_AI"},
    )
    game_id = create_response.json()["id"]

    client.post(
        f"/api/games/{game_id}/moves",
        json={"row": 7, "col": 7},
    )

    response = client.post(
        f"/api/games/{game_id}/ai-move",
        json={"difficulty": "easy"},
    )

    assert response.status_code == 400
    assert "already occupied" in response.json()["detail"]


@pytest.mark.parametrize("difficulty", ["Easy", "MEDIUM", "impossible"])
def test_ai_move_rejects_invalid_difficulty(difficulty):
    create_response = client.post(
        "/api/games",
        json={"mode": "HUMAN_VS_AI"},
    )
    game_id = create_response.json()["id"]

    response = client.post(
        f"/api/games/{game_id}/ai-move",
        json={"difficulty": difficulty},
    )

    assert response.status_code == 422
