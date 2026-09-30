from fastapi.testclient import TestClient

from app.main import app


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