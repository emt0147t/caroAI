from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_serves_frontend_homepage():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Cờ Caro AI - Bắt đầu</title>" in response.text


def test_frontend_history_page_is_served():
    response = client.get("/history.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Lịch sử" in response.text


def test_frontend_game_page_and_assets_are_served():
    game_page = client.get("/trong_tran/index.html")
    tokens = client.get("/tokens.css")

    assert game_page.status_code == 200
    assert "text/html" in game_page.headers["content-type"]
    assert tokens.status_code == 200
    assert "text/css" in tokens.headers["content-type"]


def test_api_health_route_is_not_shadowed_by_static_frontend():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
